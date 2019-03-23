from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import MySQLdb

def heat (request):
    return render(request, 'heat.html')

db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
cursor = db.cursor()

@csrf_exempt
def heat_ajax (request):
    if request.method == "POST":
        if request.POST["istek"] == "PLATabla":
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
            db.commit()

        elif request.POST["istek"] == "ABSTabla":
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
            db.commit()

        elif request.POST["istek"] == "PLANozul":
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

        elif request.POST["istek"] == "ABSNozul":
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

        elif request.POST["istek"] == "TablaOFF":
            sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M140S0',0);"
            cursor.execute(sql)
            db.commit()

        elif request.POST["istek"] == "NozulOFF":
            sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M104S0',0);"
            cursor.execute(sql)
            db.commit()

        elif request.POST['istek'] == "TablaCustom":
            sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M140S" + request.POST['val'] + "',0);"
            cursor.execute(sql)
            db.commit()

        elif request.POST["istek"] == "NozulCustom":
            sql = "INSERT INTO ArdCmd (cmd, sended) VALUES ('M104S" + request.POST['val'] + "',0);"
            cursor.execute(sql)
            db.commit()

    return HttpResponse("True")