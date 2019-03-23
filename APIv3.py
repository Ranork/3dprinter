import serial
import time
import MySQLdb
import os
import logging
import threading

# --------- AYARLAR --------- #

timeForControl = 3 #Isı ve Koordinat kontrollerinin zaman aralığı (saniye)
queue = 0 # Bekleyen komut sayısı (0 olarak bırakılmalı)
maxQueue = 5 # Maksimum bekletilebilecek komut sayısı
printLine = 0 # toplam yazdırılacak satır sayısı
printedLine = 0 # yazdırılmış satır sayısı
printFile = "" # yazdırılacak dosyanın konumu
lines = [] # yazdırılacak dosya

# --------- ------- --------- #

logging.basicConfig(filename='kayitlar.log', level=logging.DEBUG)

arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=.1)

time.sleep(1)

print("")
print("----------------------------------------")
print("-- Printer API Basariyla Calistirildi.")
print("-- Developed by Ranork for ARGESTA")
print("-- ")
print("-- PID: " + str(os.getpid()))
print("----------------------------------------")
print("")

db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
cursor = db.cursor()


now = int(time.time())

print("Database Bağlantısı Yapıldı.")

sql = "Delete From ArdCmd;"
cursor.execute(sql)
db.commit()

print("Bekleyen Komutlar Temizlendi.")

sql = "UPDATE OPT SET OptVal = '" + str(os.getpid()) + "' Where OptID = 'APIProcID';"
cursor.execute(sql)
db.commit()

print("PID Kaydedildi.")

print("")


# No Returns
def commandSend (command):
    sendcmd = command + "\n"
    sendcmdbyte = bytes(sendcmd, 'utf-8')
    arduino.write(sendcmdbyte)
    print(">> " + command)
    logging.debug(">> " + command)


# Returns String
def readArduino ():

    y = True
    cevap = ""

    while y:
        data = arduino.readline()[:-1]
        data = data.decode('utf-8')
        if data != "":
            cevap = data
            print("<< " + cevap)
        else:
            y = False

    return cevap


# No Returns
def controlTemp ():
    commandSend("M105")
    y = True
    cevap = ""
    counterA = 0
    while y:
        data = arduino.readline()[:-1]
        data = data.decode('utf-8')
        counterA += 1
        if data != "" and not data.startswith("echo") and not data == "ok" and data.startswith("ok") or "T:" in data and "B:" in data:
            cevap = data
            print("<< " + cevap)
            y = False
        elif counterA >= 10:
            y = False
    if counterA >= 10:
        return None
    ETempA = cevap.find("T:") + 2
    ETempZ = cevap.find("B:") - 1

    ETempCurrent, ETempTarget = cevap[ETempA:ETempZ].replace(" ", "").split("/")

    BTempA = cevap.find("B:") + 2
    BTempZ = cevap.find("@:") - 1

    BTempCurrent, BTempTarget = cevap[BTempA:BTempZ].replace(" ", "").split("/")

    if str(ETempTarget) == "0.00":
        ETempTarget = "Kapali"

    if str(BTempTarget) == "0.00":
        BTempTarget = "Kapali"

    if float(ETempCurrent) < 0:
        ETempCurrent = 0

    if float(BTempCurrent) < 0:
        BTempCurrent = 0


    sql = "UPDATE ArdGosterge SET ETemp = '" + str(ETempCurrent) + "', ETar = '" + str(ETempTarget) + \
          "', BTemp = '" + str(BTempCurrent) + "', BTar = '" + str(BTempTarget) + "' WHERE ID = 1"
    cursor.execute(sql)
    db.commit()


# No Returns
def controlCoordinates ():
    commandSend("M114")

    y = True
    cevap = ""
    counterA = 0

    while y:
        data = arduino.readline()[:-1]
        data = data.decode('utf-8')
        counterA += 1
        if data.startswith('X:'):
            cevap = data
            print("<< " + cevap)
            y = False
        elif counterA >= 10:
            y = False

    if counterA >= 10:
        return None

    Countst = cevap.find("C") - 1

    XkoorA = cevap[:Countst].find("X:") + 2
    XKoorZ = cevap[:Countst].find("Y:") - 1
    Xkoor = cevap[XkoorA:XKoorZ]

    YkoorA = cevap[:Countst].find("Y:") + 2
    YKoorZ = cevap[:Countst].find("Z:") - 1
    Ykoor = cevap[YkoorA:YKoorZ]

    ZkoorA = cevap[:Countst].find("Z:") + 2
    ZKoorZ = cevap[:Countst].find("E:") - 1
    Zkoor = cevap[ZkoorA:ZKoorZ]

    sql = "UPDATE ArdGosterge SET Koor_X = '" + str(Xkoor) + "', Koor_Y = '" + str(Ykoor) + "', Koor_Z = '" + \
          str(Zkoor) + "' WHERE ID=1;"
    cursor.execute(sql)
    db.commit()


# No Returns
def sendManuelCommands ():
    sql = "SELECT cmd,ID FROM ArdCmd WHERE sended = 0 ORDER BY ID ASC LIMIT 1;"
    cmd = ""
    cmdID = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            cmd = row[0]
            cmdID = row[1]
    except:
        print("SQL ERROR #S02")

    if cmd != "":
        commandSend(cmd)
        readArduino()
    if cmdID != "":
        sql = "UPDATE ArdCmd SET sended = 1 WHERE ID = " + str(cmdID) + ";"
        cursor.execute(sql)
        db.commit()


# Returns True False
def isPrinting ():
    db1 = MySQLdb.connect("localhost", "apiagent1", "api1", "ARG")
    cursor1 = db.cursor()

    sql = "SELECT OptVal FROM OPT WHERE OptID = 'Printing';"
    Printing = ""
    try:
        cursor1.execute(sql)
        results = cursor1.fetchall()
        for row in results:
            Printing = row[0]
    except:
        print("SQL ERROR #S01")

    db1.commit()

    if Printing == "False":
        return False
    elif Printing == "True":
        return True


# Controller Thread
def _generalcontroller():
    while True:
        controlTemp()
        controlCoordinates()
        time.sleep(1)

def _commandSender():
    while True:
        # Yazdırılmıyorsa özel komutları sql den yolla
        if isPrinting() == False:
            sendManuelCommands()
        time.sleep(timeForControl/2)
        # Yazdırma işleminde ise dosyadan komutları gönder


# Arduino başlangıç tanıtımını okut
starterline = 0
while starterline <= 20:
    readArduino()
    starterline += 1

th_controller = threading.Thread(target=_generalcontroller)
th_sender = threading.Thread(target=_commandSender)

th_controller.start()
th_sender.start()