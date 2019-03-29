import pymysql

db = pymysql.connect(host='localhost',
                     user='pyt',
                     password='pytpass',
                     db='ARG',
                     autocommit=True)
cursor = db.cursor()

sql = "SELECT OptVal From OPT Where OptID = 'PrintFileLoc';"
printFile = ""
try:
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        printFile = row[0]
except:
    asda = ""

print(printFile)