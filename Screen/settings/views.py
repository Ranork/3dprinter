from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import MySQLdb

db = MySQLdb.connect("localhost", "pyt", "pytpass", "ARG")
cursor = db.cursor()

def settingspage (request):

    sql = "SELECT OptVal From OPT Where OptID = 'FilamentType'"
    FilType = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            FilType = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal From OPT Where OptID = 'TablaPLA'"
    TablaPLA = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            TablaPLA = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal From OPT Where OptID = 'NozulPLA'"
    NozulPLA = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            NozulPLA = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal From OPT Where OptID = 'TablaABS'"
    TablaABS = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            TablaABS = row[0]
    except:
        asda = ""

    sql = "SELECT OptVal From OPT Where OptID = 'NozulABS'"
    NozulABS = ""
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            NozulABS = row[0]
    except:
        asda = ""

    context = {
        "FilamentType": FilType,
        "PLATabla": TablaPLA,
        "PLANozul": NozulPLA,
        "ABSTabla": TablaABS,
        "ABSNozul": NozulABS
    }
    return render(request, 'settings.html', context)

@csrf_exempt
def settings_ajax (request):
    if request.method == 'POST':
        if request.POST['set'] == "all":
            sql = "UPDATE OPT SET OptVal = '" + request.POST['PLANozul'] + "' WHERE OptID = 'NozulPLA';"
            cursor.execute(sql)
            sql = "UPDATE OPT SET OptVal = '" + request.POST['PLATabla'] + "' WHERE OptID = 'TablaPLA';"
            cursor.execute(sql)
            sql = "UPDATE OPT SET OptVal = '" + request.POST['ABSNozul'] + "' WHERE OptID = 'NozulABS';"
            cursor.execute(sql)
            sql = "UPDATE OPT SET OptVal = '" + request.POST['ABSTabla'] + "' WHERE OptID = 'TablaABS';"
            cursor.execute(sql)
            sql = "UPDATE OPT SET OptVal = '" + request.POST['FilamentType'] + "' WHERE OptID = 'FilamentType';"
            cursor.execute(sql)
            db.commit()
        else:
            return HttpResponse("False")
        return HttpResponse("True")