from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import MySQLdb

def motion (request):
    return render(request, 'motion.html')

@csrf_exempt
def customcmd(request):

    db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
    cursor = db.cursor()

    if request.method=='POST':
        if request.POST['cmd'] == "preheatON":
            sql = "SELECT OptVal From OPT Where OptID = 'FilamentType'"
            FilType = ""
            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    FilType = row[0]
            except:
                asda = ""

            if FilType == "PLA":
                sql = "SELECT OptVal From OPT Where OptID = 'TablaPLA'"
                TablaPLA = ""
                try:
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    for row in results:
                        TablaPLA = row[0]
                except:
                    asda = ""

                sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M140S" + TablaPLA + "',0);"
                cursor.execute(sql)

                sql = "SELECT OptVal From OPT Where OptID = 'NozulPLA'"
                NozulPLA = ""
                try:
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    for row in results:
                        NozulPLA = row[0]
                except:
                    asda = ""

                sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M104S" + NozulPLA + "',0);"
                cursor.execute(sql)


                db.commit()
                return HttpResponse("Başarılı")
            else:
                sql = "SELECT OptVal From OPT Where OptID = 'TablaABS'"
                TablaABS = ""
                try:
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    for row in results:
                        TablaABS = row[0]
                except:
                    asda = ""

                sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M140S" + TablaABS + "',0);"
                cursor.execute(sql)

                sql = "SELECT OptVal From OPT Where OptID = 'NozulABS'"
                NozulABS = ""
                try:
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    for row in results:
                        NozulABS = row[0]
                except:
                    asda = ""

                sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M104S" + NozulABS + "',0);"
                cursor.execute(sql)

                db.commit()
                return HttpResponse("Başarılı")

        elif request.POST['cmd'] == "preheatOFF":
            sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M104S0',0);"
            cursor.execute(sql)
            sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M140S0',0);"
            cursor.execute(sql)

            db.commit()
            return HttpResponse("Başarılı")

        elif request.POST['cmd'] is not None:
            sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('" + request.POST['cmd'] + "',0);"
            cursor.execute(sql)
            db.commit()
            return HttpResponse("Başarılı")