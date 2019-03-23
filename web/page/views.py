from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import MySQLdb
import os
import datetime
import ntpath
import time
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import math

def gcodetimecalc(fileloc):
    # -*-coding:utf-8-*-
    import os
    import math

    fileloc = os.path.join(settings.MEDIA_ROOT, str(fileloc))

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

@csrf_exempt
def page (request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)


        old_file = os.path.join(settings.MEDIA_ROOT, str(myfile.name))
        printtime = gcodetimecalc(myfile.name)
        new_file_name = str(myfile.name).split(".")[0] + "_ARG03" + str(printtime) + "." + str(myfile.name).split(".")[1]
        new_file = os.path.join(settings.MEDIA_ROOT, new_file_name)

        os.rename(old_file, new_file)

    gcodes = []
    gcodedates = []

    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for file in files:
            if file.endswith(".gcode"):
                zz = datetime.datetime.fromtimestamp(
                    int(os.path.getmtime(os.path.join(root, file)))
                ).strftime('%d.%m.%Y')
                appended_filename = str(file).replace(".gcode", "")
                numofend = appended_filename.find("_ARG03")
                dakika = int(appended_filename[numofend+6:])
                saat = int(dakika/60)
                dakika = dakika - (saat * 60)
                gcodes.append([appended_filename[:numofend], zz, file, str(saat) + " Saat " + str(dakika) + " Dakika"])

    context = {
        "gcodes": gcodes,
    }
    return render(request, 'index.html', context)

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

    newans = str(ETempCurrent) + " ℃*" + str(ETempTarget) + "*" + str(BTempCurrent) + " ℃*" + str(BTempTarget) + "*" + str(Koor_X) + "*" + str(Koor_Y) + "*" + str(Koor_Z)

    if request.method=='POST':
        if request.POST['istek'] == 'answer':
            return HttpResponse(str(newans))
        elif request.POST['istek'] == 'removefile':
            filename = request.POST['filename']
            fileloc = ""
            for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                for file in files:
                    if file == filename:
                        fileloc = os.path.join(root, file)
            os.remove(fileloc)
            return HttpResponse("True")



@csrf_exempt
def preheat(request):
    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    TablaABS = ""
    TablaPLA = ""
    NozulABS = ""
    NozulPLA = ""

    sql = "SELECT OptVal FROM OPT Where OptID = 'TablaABS';"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            TablaABS = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal FROM OPT Where OptID = 'TablaPLA';"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            TablaPLA = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal FROM OPT Where OptID = 'NozulABS';"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            NozulABS = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal FROM OPT Where OptID = 'NozulPLA';"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            NozulPLA = row[0]
    except:
        asda = ""

    if request.method=='POST':

        if request.POST['istek'] == 'NOZULABS':
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('M104S" + str(NozulABS) + "',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")

        if request.POST['istek'] == 'BEDABS':
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('M140S" + str(TablaABS) + "',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")

@csrf_exempt
def setbedtemp(request):

    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    if request.method=='POST':

        if request.POST['derece'] == '0':
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('M140S0',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")
        else:
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('M140S" + str(request.POST['derece']) + "',0)"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")

@csrf_exempt
def setexttemp(request):

    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    if request.method=='POST':

        if request.POST['derece'] == '0':
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('M104S0',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")
        else:
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('M104S" + str(request.POST['derece']) + "',0)"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")

@csrf_exempt
def customcmd(request):

    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    if request.method=='POST':
        if request.POST['cmd'] is not None:
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('" + request.POST['cmd'] + "',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")

@csrf_exempt
def manualmove(request):

    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    if request.method=='POST':

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

        if request.POST['target'] == 'y':
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('G91',0);"
            cursor.execute(sql)
            db.commit()
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('G1Y" + request.POST['distance'] + "',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")
        elif request.POST['target'] == 'x':
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('G91',0);"
            cursor.execute(sql)
            db.commit()
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('G1X" + request.POST['distance'] + "',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")
        elif request.POST['target'] == 'z':
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('G91',0);"
            cursor.execute(sql)
            db.commit()
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('G1Z" + request.POST['distance'] + "',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")
        elif request.POST['target'] == 'e':
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('G91',0);"
            cursor.execute(sql)
            db.commit()
            sql = "INSERT INTO ArdCmd (cmd,sended) VALUES ('G1E" + request.POST['distance'] + "',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")


@csrf_exempt
def printjob (request):
    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()
    if request.method == 'GET':
        sql = "SELECT OptVal FROM OPT Where OptID = 'Printing';"
        isPrinting = False
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                isPrinting = str(row[0])
        except:
            asda = ""

        filename = request.GET.get('filenames')
        if isPrinting == "False":
            fileloc = "";

            for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                for file in files:
                    if file == filename:
                        fileloc = os.path.join(root, file)

            # num_lines = sum(1 for line in open(fileloc))



            sql = "UPDATE OPT SET OptVal = '" + fileloc + "' WHERE OptID='PrintFileLoc'"
            cursor.execute(sql)
            sql = "UPDATE OPT SET OptVal = 'True' WHERE OptID='Printing'"
            cursor.execute(sql)
            sql = "UPDATE OPT SET OptVal = '" + str(int(time.time())) + "' WHERE OptID = 'PrintStartTime'"
            cursor.execute(sql)
            db.commit()

        # num_lines = sum(1 for line in open(fileloc))

        # sql = "UPDATE OPT SET OptVal = '" + str(num_lines) + "' WHERE OptID = 'PrintLine'"
        # cursor.execute(sql)
        # sql = "UPDATE OPT SET OptVal = '0' WHERE OptID = 'PrintedLine'"
        # cursor.execute(sql)
        # db.commit()

        starttime = round(datetime.datetime.now().timestamp())

        # f = open(fileloc, 'r')
        # fileline = f.readlines()
        # f.close()
        #
        # i = 0
        # id = 0
        # while i <= num_lines-1:
        #     fileline[i] = fileline[i].replace("\n", "")
        #     fileline[i] = fileline[i].replace(" ", "")
        #     if fileline[i].startswith(";"):
        #         i = i + 1
        #     else:
        #         sql = "INSERT INTO PrintJob (ID,CODE,DATE,OK) VALUES ('" + str(id) + "','" + str(fileline[i]) + "','" + time.strftime('%Y-%m-%d %H:%M:%S') + "',0);"
        #         cursor.execute(sql)
        #         i = i + 1
        #         id = id + 1

        return render(request, 'printjob.html', {"file": filename})


@csrf_exempt
def form_ajax_printjob(request):
    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    printstart = 0
    printed = 0
    willprint = 0

    sql = "SELECT OptVal FROM OPT Where OptID = 'PrintStartTime';"

    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            printstart = int(row[0])
    except:
        asda = ""

    sql = "SELECT OptVal From OPT WHERE OptID = 'PrintFileLoc';"
    fileloc = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            fileloc = row[0]
    except:
        fileloc = ""
        print("SQL CONNECTION FAILED")

    file = ntpath.basename(fileloc)
    appended_filename = str(file).replace(".gcode", "")
    numofend = appended_filename.find("_ARG03")
    dakika = int(appended_filename[numofend + 6:])
    willprint = dakika * 60

    printed = int(time.time()) - int(printstart)

    printpercent = (printed / willprint) * 100

    if printpercent > 99:
        printpercent = 99


    newans = str(printpercent)

    if request.method == 'POST':
        if request.POST['istek'] == 'percentage':
            return HttpResponse(str(newans))
        if request.POST['istek'] == 'time':
            return HttpResponse(str(printed))
        if request.POST['istek'] == 'isPrinting':
            sql = "SELECT OptVal FROM OPT Where OptID = 'Printing'"
            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    if row[0] == "False":
                        return HttpResponse("False")
                    elif row[0] == "Paused":
                        sql = "SELECT OptVal FROM OPT Where OptID = 'PrintFileLoc'"
                        try:
                            cursor.execute(sql)
                            results = cursor.fetchall()
                            for row in results:
                                return HttpResponse("Paused*" + row[0])
                        except:
                            asda = ""
                    else:
                        sql = "SELECT OptVal FROM OPT Where OptID = 'PrintFileLoc'"
                        try:
                            cursor.execute(sql)
                            results = cursor.fetchall()
                            for row in results:
                                return HttpResponse("True*" + row[0])
                        except:
                            asda = ""
            except:
                return HttpResponse("Error")
        if request.POST['istek'] == 'PrintStop':
            sql = "UPDATE OPT SET OptVal = 'False' Where OptID = 'Printing'"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("True")
        if request.POST['istek'] == 'PrintPause':
            sql = "UPDATE OPT SET OptVal = 'Paused' Where OptID = 'Printing'"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("True")
        if request.POST['istek'] == 'PrintContinue':
            sql = "UPDATE OPT SET OptVal = 'True' Where OptID = 'Printing'"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("True")

@csrf_exempt
def sett(request):
    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    TablaABS = ""
    TablaPLA = ""
    NozulABS = ""
    NozulPLA = ""

    sql = "SELECT OptVal FROM OPT Where OptID = 'TablaABS';"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            TablaABS = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal FROM OPT Where OptID = 'TablaPLA';"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            TablaPLA = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal FROM OPT Where OptID = 'NozulABS';"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            NozulABS = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal FROM OPT Where OptID = 'NozulPLA';"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            NozulPLA = row[0]
    except:
        asda = ""

    content = {
        "TablaABS": TablaABS,
        "TablaPLA": TablaPLA,
        "NozulABS": NozulABS,
        "NozulPLA": NozulPLA
    }

    return  render(request, 'settings.html', content)

@csrf_exempt
def settingsAjax (request):
    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    if request.method == 'POST':
        if request.POST['istek'] == 'save':
            sql = "UPDATE OPT SET OptVal='" + request.POST['TablaABS'] + "' Where OptID='TablaABS'"
            cursor.execute(sql)
            sql = "UPDATE OPT SET OptVal='" + request.POST['TablaPLA'] + "' Where OptID='TablaPLA'"
            cursor.execute(sql)
            sql = "UPDATE OPT SET OptVal='" + request.POST['NozulABS'] + "' Where OptID='NozulABS'"
            cursor.execute(sql)
            sql = "UPDATE OPT SET OptVal='" + request.POST['NozulPLA'] + "' Where OptID='NozulPLA'"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Success")