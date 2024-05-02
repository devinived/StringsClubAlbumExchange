import sqlite3
OPENORCLOSED = "additional dbs/openorclosed.db"

def make_table():
    conn = sqlite3.connect(OPENORCLOSED)
    c = conn.cursor()

    c.execute("""CREATE TABLE if not exists exchanges (
              exchange_date STR,
              status BOOL)""")
def inDB(date):
    date=date.lower()
    conn = sqlite3.connect(OPENORCLOSED)
    c = conn.cursor()

    c.execute("""SELECT * FROM exchanges WHERE exchange_date = (?)""",(date,))
    
    if c.fetchall() == []:
        return False
    else:
        return True

def add_one(date, status = True):
    conn = sqlite3.connect(OPENORCLOSED)
    c = conn.cursor()
    c.execute("""INSERT INTO exchanges VALUES (?,?)""",(date,status))
    conn.commit()
    conn.close()

def show_all(date):
    conn = sqlite3.connect(OPENORCLOSED)
    c = conn.cursor()
    c.execute("SELECT exchange_date FROM exchanges")
    items = c.fetchall()
    return items

def getStatus(date):
    conn = sqlite3.connect(OPENORCLOSED)
    c = conn.cursor()    

    c.execute("SELECT status fROM exchanges WHERE exchange_date = (?)", (date,))
    result = c.fetchall()
    result = str(result).replace("[","").replace("(","").replace("]","").replace(")","")

    if "True" in result:
        return True
    elif "1" in result:
        return True
    else:
        return False

def setStatus(date, status):
    if not inDB(date):
        return False
    status = bool(status)
    conn = sqlite3.connect(OPENORCLOSED)
    c = conn.cursor()

    c.execute("UPDATE exchanges SET status = (?) WHERE exchange_date = (?)",(status, date))
    
    conn.commit()
    conn.close()