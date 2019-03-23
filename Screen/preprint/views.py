from django.shortcuts import render, HttpResponse
import os
import datetime
import time
from django.views.decorators.csrf import csrf_exempt
import MySQLdb
from shutil import copyfile

db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
cursor = db.cursor()

def gcodetimecalc(fileloc):
    # -*-coding:utf-8-*-
    import os
    import math

    fileloc = os.path.join(str(fileloc))

    num_lines = sum(1 for line in open(fileloc))

    f = open(fileloc, 'r')
    fileline = f.readlines()
    f.close()

    i = 0
    loop = True

    X = 0.000
    Y = 0.000
    Z = 0.000
    F = 0.000
    E = 0.000
    a = 76
    acc = 3000

    TotalTime = 0.000

    while loop:

        if i >= num_lines - 1:
            loop = False

        Xn = 999.999
        Yn = 999.999
        Zn = 999.999
        En = 999.999
        LineTime = 0.000
        TotalDist = 0.000

        if fileline[i] == "" or fileline[i].startswith(";") or len(fileline[i]) <= 2:
            i += 1
        elif fileline[i].startswith("G1"):
            # print(fileline[i][:-1])

            for cc in fileline[i][:-1].split(" "):
                if cc.startswith("X"):
                    Xn = float(cc.replace("X", ""))
                elif cc.startswith("Y"):
                    Yn = float(cc.replace("Y", ""))
                elif cc.startswith("Z"):
                    Zn = float(cc.replace("Z", ""))
                elif cc.startswith("F"):
                    F = float(cc.replace("F", ""))
                elif cc.startswith("E"):
                    En = float(cc.replace("E", ""))

            DistanceX = 0.000
            DistanceY = 0.000

            if Xn != 999.999:
                DistanceX = abs(X - Xn)
            if Yn != 999.999:
                DistanceY = abs(Y - Yn)

            if DistanceX > 0.000:
                X = Xn
                if DistanceY > 0.000:
                    Y = Yn
                    TotalDist = math.sqrt((DistanceX ** 2) + (DistanceY ** 2))
                else:
                    TotalDist = DistanceX
            elif DistanceY > 0.000:
                Y = Yn
                TotalDist = DistanceY

            if Zn != 999.999:
                TotalDist = abs(Z - Zn)
                Z = Zn

            LineTime = TotalDist / (F / a)
            TotalTime = TotalTime + LineTime

            i += 1
        else:
            i += 1
    TotalTime = int(round(TotalTime/60))
    return TotalTime

def preprint (request):
    gcodes = []

    for root, dirs, files in os.walk("/home/ranork/Desktop/argesta/web/media"):
        for file in files:
            if file.endswith(".gcode"):
                zz = datetime.datetime.fromtimestamp(
                    int(os.path.getmtime(os.path.join(root, file)))
                ).strftime('%d.%m.%Y')
                appended_filename = str(file).replace(".gcode", "")
                numofend = appended_filename.find("_ARG03")
                dakika = int(appended_filename[numofend + 6:])
                saat = int(dakika / 60)
                dakika = dakika - (saat * 60)
                gcodes.append([appended_filename[:numofend], zz, file, str(saat) + " Saat " + str(dakika) + " Dakika"])

    context = {
        "gcodes": gcodes,
    }
    return render(request, 'preprint.html', context)

def printjob (request):
    sql = "SELECT OptVal From OPT Where OptID = 'PrintFileLoc'"
    PrintFileLoc = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            PrintFileLoc = row[0]
    except:
        asda = ""

    splitedFileLoc = PrintFileLoc.split("/")
    fullFileName = splitedFileLoc[len(splitedFileLoc)-1]

    appended_filename = str(fullFileName).replace(".gcode", "")
    numofend = appended_filename.find("_ARG03")
    filename = appended_filename[:numofend]
    dakika = int(appended_filename[numofend + 6:])

    context = {
        "filename": filename,
        "timestamp": str(dakika * 60)
    }

    return render(request, 'printjob.html', context)

@csrf_exempt
def form_ajax(request):
    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    sql = "SELECT ETemp, ETar, BTemp, BTar FROM ArdGosterge Where ID = 1;"

    ETempCurrent = ""
    ETempTarget = ""
    BTempCurrent = ""
    BTempTarget = ""


    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            ETempCurrent = row[0]
            ETempTarget = row[1]
            BTempCurrent = row[2]
            BTempTarget = row[3]
    except:
        asda = ""

    print("ETempCurrent: " + ETempCurrent)
    print("ETempTarget: " + ETempTarget)
    print("BTempCurrent: " + BTempCurrent)
    print("BTempTarget: " + BTempTarget)

    if str(BTempTarget) != "Kapali":
        BTempTarget = BTempTarget + " ℃"
    if str(ETempTarget) != "Kapali":
        ETempTarget = ETempTarget + " ℃"

    sql = "SELECT Koor_X, Koor_Y, Koor_Z FROM ArdGosterge Where ID = 1;"

    Koor_X = ""
    Koor_Y = ""
    Koor_Z = ""

    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            Koor_X = row[0]
            Koor_Y = row[1]
            Koor_Z = row[2]
    except:
        asda = ""


    newans = str(ETempCurrent) + " ℃*" + str(ETempTarget) + "*" + str(BTempCurrent) + " ℃*" + str(BTempTarget) + "*"\
             + str(Koor_X) + "*" + str(Koor_Y) + "*" + str(Koor_Z)
    db.commit()
    cursor.close()

    if request.method=='POST':
        if request.POST['istek'] == 'answer':
            return HttpResponse(str(newans))
        elif request.POST['istek'] == 'removefile':
            filename = request.POST['filename']
            fileloc = ""
            for root, dirs, files in os.walk("/home/ranork/Desktop/argesta/web/media"):
                for file in files:
                    if file == filename:
                        fileloc = os.path.join(root, file)
            os.remove(fileloc)
            return HttpResponse("True")
        elif request.POST['istek'] == 'stop':
            sql = "UPDATE OPT SET OptVal = 'False' WHERE OptID = 'Printing';"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("True")
        elif request.POST['istek'] == "isPrinting":
            sql = "SELECT OptVal From OPT Where OptID = 'Printing'"
            Printing = ""
            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    Printing = row[0]
            except:
                asda = ""
            if Printing == "False":
                return HttpResponse("False")
            else:
                return HttpResponse("True")
        elif request.POST["istek"] == "printstate":
            sql = "SELECT OptVal FROM OPT WHERE OptID = 'PrintedLine'"

            PrintedLine = ""

            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    PrintedLine = row[0]
            except:
                asda = ""

            sql = "SELECT OptVal FROM OPT WHERE OptID = 'PrintLine'"

            PrintLine = ""

            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    PrintLine = row[0]
            except:
                asda = ""

            sql = "SELECT OptVal From OPT Where OptID = 'PrintFileLoc'"
            PrintFileLoc = ""
            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    PrintFileLoc = row[0]
            except:
                asda = ""

            splitedFileLoc = PrintFileLoc.split("/")
            fullFileName = splitedFileLoc[len(splitedFileLoc) - 1]

            appended_filename = str(fullFileName).replace(".gcode", "")
            numofend = appended_filename.find("_ARG03")
            dakika = int(appended_filename[numofend + 6:])

            sql = "SELECT OptVal From OPT Where OptID = 'PrintStartTime'"
            PrintStartTime = ""
            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    PrintStartTime = row[0]
            except:
                asda = ""

            passedTime = int(time.time()) - int(PrintStartTime)
            remainingTime = str(float(dakika) * 60 - float(passedTime))

            answer = str(PrintLine) + "*" + str(PrintedLine) + "*" + str(remainingTime)
            return HttpResponse(answer)



@csrf_exempt
def startPrint(request):

    if request.POST['file'] is not None:
        filename = request.POST['file']
        fileloc = ""
        for root, dirs, files in os.walk("/home/ranork/Desktop/argesta/web/media"):
            for file in files:
                if file == filename:
                    fileloc = os.path.join(root, file)

        sql = "UPDATE OPT SET OptVal = '" + fileloc + "' WHERE OptID = 'PrintFileLoc'"
        cursor.execute(sql)
        sql = "UPDATE OPT SET OptVal = 'True' WHERE OptID = 'Printing'"
        cursor.execute(sql)
        sql = "UPDATE OPT SET OptVal = '" + str(int(time.time())) + "' WHERE OptID = 'PrintStartTime'"
        cursor.execute(sql)
        db.commit()
        return HttpResponse("True")

def usb(request):
    gcodes = []

    for root, dirs, files in os.walk("/media/"):
        for file in files:
            if file.endswith(".gcode"):
                appended_filename = str(file).replace(".gcode", "")
                gcodes.append([appended_filename])

    context = {
        "gcodes": gcodes,
    }
    return render(request, 'usb.html', context)

@csrf_exempt
def usb_ajax (request):
    if request.method == "POST":
        if request.POST['istek'] == "SaveFile":
            filename = request.POST['file']
            fileloc = ""
            for root, dirs, files in os.walk("/media"):
                for file in files:
                    if file == filename + ".gcode":
                        fileloc = os.path.join(root, file)
                        copyfile(fileloc, "/home/ranork/Desktop/argesta/web/media/" + filename + "_ARG03"
                                 + str(gcodetimecalc(fileloc)) + ".gcode")
    return HttpResponse("True")
