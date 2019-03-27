import serial
import time
import MySQLdb
import os
import logging
import threading

# --------- AYARLAR --------- #

timeForControl = 2 #Isı ve Koordinat kontrollerinin zaman aralığı (saniye)
printQueue = 0 # Bekleyen komut sayısı (0 olarak bırakılmalı)
maxQueue = 5 # Maksimum bekletilebilecek komut sayısı
printLine = 0 # toplam yazdırılacak satır sayısı
printedLine = 0 # yazdırılmış satır sayısı
printFile = "" # yazdırılacak dosyanın konumu
lines = [] # yazdırılacak dosya
printStarted = False # yazdırma işlemi program tarafından başlatıldı mı

controllerThreadWorking = False
printThreadWorking = False
printReaderThreadWorking = False

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


# Returns Answer as a String
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


# No Returns
def sendManuelCommands ():
    sql = "SELECT cmd,ID FROM ArdCmd WHERE sended = 0;"
    cmd = ""
    cmdID = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            cmd = row[0]
            cmdID = row[1]
            if cmd != "":
                commandSend(cmd)
                readArduino()
            if cmdID != "":
                sql = "UPDATE ArdCmd SET sended = 1 WHERE ID = " + str(cmdID) + ";"
                cursor.execute(sql)
    except:
        print("SQL ERROR #S02")
        db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")


# Returns True False
def isPrinting ():

    sql = "SELECT OptVal FROM OPT WHERE OptID = 'Printing';"
    Printing = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            Printing = row[0]
    except:
        print("SQL ERROR #S01")
        db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")

    db.commit()

    if Printing == "False":
        return False
    elif Printing == "True":
        return True


# Starts printing queue
def startPrint():
    global controllerThreadWorking
    global printThreadWorking
    global printStarted
    global lines

    sql = "SELECT OptVal From OPT Where OptID = 'PrintFileLoc'"
    printFile = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            printFile = row[0]
    except:
        asda = ""

    print(">> PRINT JOB STARTING: " + printFile)
    logging.debug("Print Job Started! -- " + printFile)

    printLine = sum(1 for line in open(printFile))

    sql = "UPDATE OPT SET OptVal = '" + str(printLine) + "' WHERE OptID = 'PrintLine'"
    cursor.execute(sql)
    sql = "UPDATE OPT SET OptVal = '20' WHERE OptID = 'PrintedLine'"
    cursor.execute(sql)
    db.commit()

    f = open(printFile, 'r')
    lines = f.readlines()
    f.close()

    printStarted = True

    # Print Threadlerini çalıştır manual controlleri kapa
    controllerThreadWorking = False
    printThreadWorking = True
    th_print.start()


# # # # # THREADS # # # # #

# Controller Thread
def _generalcontroller():
    global db
    global cursor

    while controllerThreadWorking:
        controlTemp()
        controlCoordinates()
        sendManuelCommands()

        try:
            db.commit()
        except:
            db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
            cursor = db.cursor()

        time.sleep(timeForControl/2)


# Print state controller
def _printState():
    while True:
        if isPrinting():
            if printStarted == False:
                startPrint()
                print("Yazdırma işlemi başlatılıyor. Satır: " + str(len(lines)))
        else:
            # Print threadini iptal et
            controllerThreadWorking = True
            printThreadWorking = False
            if th_controller.is_alive() == False:
                th_controller.start()
            print("Yazdırma işlemi yok")
        time.sleep(timeForControl*2)


# Print thread
def _print():
    global printedLine
    global printQueue
    global printReaderThreadWorking

    while printLine <= printedLine:
        if printThreadWorking == False:
            return

        guncelSatir = lines[printedLine]

        if "Z" in guncelSatir:
            whereisZ = guncelSatir.find("Z")
            whereisF = guncelSatir.find("F")
            sql = "UPDATE ArdGosterge SET Koor_Z = '" + guncelSatir[whereisZ + 1:whereisF - 1] + "'"

            cursor.execute(sql)
            db.commit()

        if guncelSatir.startswith(";") or guncelSatir == "" or len(guncelSatir) <= 3:
            printedLine += 1

        elif printedLine <= 20:
            commandSend(guncelSatir)
            print("[ " + str(printedLine) + " ]")
            readArduino()

            printedLine += 1

        else:
            if printQueue == 0:
                printReaderThreadWorking = True
                th_printReader.start()
                printQueue = 1
                time.sleep(1)
            elif printQueue <= maxQueue:
                commandSend(guncelSatir)
                print("[ " + str(printedLine) + " ]")
                printedLine += 1
                printQueue += 1


# Print reader thread (controlling the queue)
def _printReader():
    global printQueue
    while True:
        if printReaderThreadWorking == False:
            return

        if printedLine >= 20:
            geridonut = readArduino()

            if "T:" in geridonut and "B:" in geridonut:
                ETempA = geridonut.find("T:") + 2
                ETempZ = geridonut.find("B:") - 1

                ETempCurrent, ETempTarget = geridonut[ETempA:ETempZ].replace(" ", "").split("/")

                BTempA = geridonut.find("B:") + 2
                BTempZ = geridonut.find("@:") - 1

                BTempCurrent, BTempTarget = geridonut[BTempA:BTempZ].replace(" ", "").split("/")

                if str(ETempTarget) == "0.00":
                    ETempTarget = "Kapali"

                if str(BTempTarget) == "0.00":
                    BTempTarget = "Kapali"

                if float(ETempCurrent) < 0:
                    ETempCurrent = 0

                if float(BTempCurrent) < 0:
                    BTempCurrent = 0

                sql = "UPDATE ArdGosterge SET ETemp = '" + str(ETempCurrent) + "', ETar = '" + str(
                    ETempTarget) + \
                      "', BTemp = '" + str(BTempCurrent) + "', BTar = '" + str(BTempTarget) + "' WHERE ID = 1"
                cursor.execute(sql)
                try:
                    db.commit()
                except:
                    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")

            elif "ok" in geridonut:
                printQueue -= 1


# Queue reporter
def _printingqueue():
    while True:
        print(str(printQueue) + " / " + str(maxQueue))

# # # # # ------- # # # # #


th_controller = threading.Thread(target=_generalcontroller)
th_print = threading.Thread(target=_print)
th_printStater = threading.Thread(target=_printState)
th_printReader = threading.Thread(target=_printReader)


# Arduino başlangıç tanıtımını okut
starterline = 0
while starterline <= 20:
    readArduino()
    starterline += 1

controllerThreadWorking = True
th_controller.start()
th_printStater.start()

