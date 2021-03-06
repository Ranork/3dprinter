import serial
import time
import os
import logging
import threading
import pymysql

# --------- SETTINGS

timeForControl = 2 #Isı ve Koordinat kontrollerinin zaman aralığı (saniye)
maxQueue = 5 # Maksimum bekletilebilecek komut sayısı
controlQueue = 0 # Beklenen kontrol sırası (0 olarak bırakılmalı)

# ---------- Constans Variables

printQueue = 0 # Bekleyen komut sayısı (0 olarak bırakılmalı)
maxControlQueue = 10 # Maksimum beklenecek kontrol
printLine = 0 # toplam yazdırılacak satır sayısı
printedLine = 0 # yazdırılmış satır sayısı
printFile = "" # yazdırılacak dosyanın konumu
lines = [] # yazdırılacak dosya
printStarted = False # yazdırma işlemi program tarafından başlatıldı mı

controllerThreadWorking = False
printThreadWorking = False
printReaderThreadWorking = False

# ------------------------

logging.basicConfig(filename='kayitlar.log', level=logging.DEBUG)

arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=.1)

time.sleep(1)

print("")
print("----------------------------------------")
print("-- Welcome to Printer API")
print("-- Developed by Ranork for ARGESTA Engineering")
print("-- ")
print("-- PID: " + str(os.getpid()))
print("----------------------------------------")
print("")

db = pymysql.connect(host='localhost',
                     user='pyt',
                     password='pytpass',
                     db='ARG',
                     autocommit=True)
cursor = db.cursor()

# Define MySQL Connection
def mysqlConn():
    global db
    global cursor
    db = pymysql.connect(host='localhost',
                         user='pyt',
                         password='pytpass',
                         db='ARG',
                         autocommit=True)
    cursor = db.cursor()

mysqlConn()

now = int(time.time())

print("Database connected.")

sql = "Delete From ArdCmd;"
cursor.execute(sql)

print("Command queue cleared.")

sql = "UPDATE OPT SET OptVal = '" + str(os.getpid()) + "' Where OptID = 'APIProcID';"
cursor.execute(sql)

print("PID Saved.")

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
    global printQueue
    global controlQueue
    global db
    global arduino

    y = True
    cevap = ""

    while y:
        data = arduino.readline()[:-1]
        data = data.decode('utf-8')
        if data != "":
            cevap = data
            print("<< " + cevap)
            if "ok" in cevap and printQueue > 0:
                printQueue -= 1
        else:
            y = False

    if "T:" in cevap and "B:" in cevap:
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

        sql = "UPDATE ArdGosterge SET ETemp = '" + str(ETempCurrent) + "', ETar = '" + str(
            ETempTarget) + \
              "', BTemp = '" + str(BTempCurrent) + "', BTar = '" + str(BTempTarget) + "' WHERE ID = 1"
        time.sleep(0.3)
        cursor.execute(sql)

        if controlQueue > 1:
            controlQueue -= 1

    elif "Error:" in cevap:
        arduino.close()
        arduino.open()

    return cevap


# No Returns
def controlTemp ():
    global controlQueue

    if controlQueue < maxQueue:
        commandSend("M105")
        readArduino()
        controlQueue += 1
    else:
        print("Arduino will be reseted after 10 seconds.")
        time.sleep(10)
        arduino.close()
        arduino.open()
        print("Arduino Reset")
        time.sleep(5)
        controlQueue = 0




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
    global db

    sql = "SELECT cmd,ID FROM ArdCmd WHERE sended = 0;"
    cmd = ""
    cmdID = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            if row[0] != "":
                cmd = row[0]
                commandSend(cmd)
                readArduino()
            if row[1] != "":
                cmdID = row[1]
                sql = "UPDATE ArdCmd SET sended = 1 WHERE ID = " + str(cmdID) + ";"
                cursor.execute(sql)
    except TypeError as e:
        print("SQL ERROR #S02")
        print(e)


# Returns True False
def isPrinting ():
    global db

    sql = "SELECT OptVal FROM OPT WHERE OptID = 'Printing';"
    Printing = ""
    try:
        time.sleep(1)
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            Printing = row[0]
    except TypeError as e:
        print("SQL ERROR #S01")
        print(e)

    if Printing == "False":
        return False
    elif Printing == "True":
        return True


# 01tarts printing queue
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

    print(">> PRINT JOB STARTING | File: " + printFile)
    logging.debug("Print Job Started! -- " + printFile)

    printLine = sum(1 for line in open(printFile))

    time.sleep(2)

    sql = "UPDATE OPT SET OptVal = '" + str(printLine) + "' WHERE OptID = 'PrintLine'"
    cursor.execute(sql)
    sql = "UPDATE OPT SET OptVal = '20' WHERE OptID = 'PrintedLine'"
    cursor.execute(sql)

    f = open(printFile, 'r')
    lines = f.readlines()
    f.close()

    printStarted = True

    # Print Threadlerini çalıştır manual controlleri kapa
    controllerThreadWorking = False
    time.sleep(3)
    printThreadWorking = True


# # # # # THREADS # # # # #

# Controller  !!! Thread NOT WORKING !!!
# def _generalcontroller():
#     global db
#     global cursor
#
#     while True:
#         if controllerThreadWorking:
#             controlTemp()
#             controlCoordinates()
#             sendManuelCommands()
#
#             time.sleep(timeForControl)


# Print state controller
def _printState():
    global controllerThreadWorking
    global printThreadWorking
    global printReaderThreadWorking
    global printedLine
    global printQueue

    while True:
        if (printThreadWorking and printedLine < 30) or (printedLine%100 == 0 and printedLine > 0):
            print("Print State Controller is Waiting")
            time.sleep(5)
        elif isPrinting():
            if printThreadWorking == False:
                startPrint()
                print("Print job detected. File line count: " + str(len(lines)))
        else:
            if printThreadWorking:
                print("Print job is canceled.")
                # Print threadini iptal et
                printThreadWorking = False
                printReaderThreadWorking = False
                time.sleep(2)
                commandSend("G28XY")
                printedLine = 0
                printQueue = 0
                print("Arduino will be reseted after 10 seconds.")
                time.sleep(10)
                arduino.close()
                arduino.open()
                print("Arduino Reset")
                time.sleep(5)

            else:
                print("There is not any Print Job")

                if th_printReader.is_alive() == False:
                    th_printReader.run()

                sendManuelCommands()
                controlTemp()
                sendManuelCommands()
                controlCoordinates()
                sendManuelCommands()
        time.sleep(timeForControl)


# Print thread
def _print():
    global printedLine
    global printQueue
    global printReaderThreadWorking
    global db

    while True:
        while printThreadWorking:
            if printLine <= printedLine:
                guncelSatir = lines[printedLine]

                if printedLine % 100 == 0 or printedLine <= 15:
                    time.sleep(0.3)
                    sql = "UPDATE OPT SET OptVal = '" + str(printedLine) + "' Where OptID = 'PrintedLine'"
                    try:
                        cursor.execute(sql)
                    except:
                        print("SQL Reconnect called!")
                        mysqlConn()
                    if printedLine % 10000 == 0:
                        printQueue = 0

                if guncelSatir.startswith(";") or guncelSatir == "" or len(guncelSatir) <= 3:
                    printedLine += 1

                else:
                    if printReaderThreadWorking == False:
                        printReaderThreadWorking = True
                        printQueue = 1
                        time.sleep(1)
                    elif printQueue <= maxQueue:
                        commandSend(guncelSatir)
                        print("[ " + str(printedLine) + " ]  Q: " + str(printQueue) + " / " + str(maxQueue))
                        printedLine += 1
                        printQueue += 1


# Print reader thread (controlling the queue)
def _printReader():
    global printQueue
    while True:
        if printReaderThreadWorking:
            cevap = readArduino()


        # if "ok" in cevap and printQueue > 0:
        #     print("printQueue -1")
        #     printQueue -= 1

# # # # # ------- # # # # #


# th_controller = threading.Thread(target=_generalcontroller)
th_print = threading.Thread(target=_print)
th_printStater = threading.Thread(target=_printState)
th_printReader = threading.Thread(target=_printReader)


# Read marlin describe lines
starterline = 0
while starterline <= 20:
    readArduino()
    starterline += 1

controllerThreadWorking = True
th_printStater.start()
# th_controller.start()
th_print.start()
th_printReader.start()