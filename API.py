import serial
import time
import MySQLdb
import os
import logging

# --------- AYARLAR --------- #
timeForControl = 3 #Isı ve Koordinat kontrollerinin zaman aralığı

# --------- ------- --------- #

logging.basicConfig(filename='kayitlar.log',level=logging.DEBUG)

arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=.1)

time.sleep(1)

print("")
print("----------------------------------------")
print("-- Printer API Basariyla Calistirildi.")
print("-- Developed by Ranork")
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
    sql = "SELECT cmd,ID FROM ArdCmd WHERE sended = 0;"
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
        print(readArduino())
    if cmdID != "":
        sql = "UPDATE ArdCmd SET sended = 1 WHERE ID = " + str(cmdID) + ";"
        cursor.execute(sql)
        db.commit()


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

    if Printing == "False":
        db.commit()
        return False
    elif Printing == "True":
        db.commit()
        return True


line = 0

while line <= 20:
    readArduino()
    line += 1

print("")

generalLoop = True


while generalLoop:

    # Belirli zaman aralıklarıyla ısı ve koordinat kontrolü
    if time.time() - now >= timeForControl:
        controlTemp()
        controlCoordinates()
        now = time.time()

    if isPrinting() == False:

        sendManuelCommands()
    else:
        sql = "SELECT OptVal From OPT Where OptID = 'PrintFileLoc'"
        PrintFileLoc = ""
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                PrintFileLoc = row[0]
        except:
            asda = ""

        print(">> PRINT JOB STARTING: " + PrintFileLoc)
        logging.debug("Print Job Started! -- " + PrintFileLoc)

        num_lines = sum(1 for line in open(PrintFileLoc))

        sql = "UPDATE OPT SET OptVal = '" + str(num_lines) + "' WHERE OptID = 'PrintLine'"
        cursor.execute(sql)
        sql = "UPDATE OPT SET OptVal = '20' WHERE OptID = 'PrintedLine'"
        cursor.execute(sql)
        db.commit()

        f = open(PrintFileLoc, 'r')
        file = f.readlines()
        f.close()

        printLoop = True
        line = 0

        while printLoop:

            print(">> " + file[line])

            if "Z" in file[line]:
                whereisZ = file[line].find("Z")
                whereisF = file[line].find("F")
                sql = "UPDATE ArdGosterge SET Koor_Z = '" + file[line][whereisZ+1:whereisF-1] + "'"

                cursor.execute(sql)
                db.commit()
            elif "Z" in file[line+1]:
                whereisZ = file[line+1].find("Z")
                whereisF = file[line+1].find("F")
                sql = "UPDATE ArdGosterge SET Koor_Z = '" + file[line+1][whereisZ+1:whereisF-1] + "'"

                cursor.execute(sql)
                db.commit()

            if line >= num_lines - 5:
                sql = "UPDATE OPT SET OptVal = 'False' WHERE OptID = 'Printing';"
                printLoop = False
                cursor.execute(sql)
                db.commit()

            # Normalin yarısı aralıklarla kontrol yap
            if int(time.time()) - now >= timeForControl * 2:
                commandSend("M105")
                commandSend("M114")

                sql = "UPDATE OPT SET OptVal = '" + str(line) + "' WHERE OptID = 'PrintedLine'"
                cursor.execute(sql)
                db.commit()

                now = time.time()
                if isPrinting() == False:
                    printLoop = False
                    db.commit()
                    commandSend("G28XY")

            else:

                if file[line].startswith(";") or file[line] == "" or len(file[line]) <= 3:
                    line += 1

                elif "G1 F" in file[line]:
                    commandSend(file[line])
                    print("[ " + str(line) + " ]")
                    readArduino()

                    line += 1

                elif line <= 20:
                    commandSend(file[line])
                    print("[ " + str(line) + " ]")
                    readArduino()

                    line += 1

                else:
                    commandSend(file[line])
                    print("[ " + str(line) + " ]")
                    commandSend(file[line+1])
                    print("[ " + str(line+1) + " ]")

                    waitingForResponse = True
                    while waitingForResponse:
                        geridonut = readArduino()
                        if geridonut == "ok":
                            waitingForResponse = False
                            readArduino()

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
                            db.commit()

                    line += 2












