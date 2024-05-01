import sqlite3
import os
from os import listdir
from os.path import isfile, join
import random
print("Connected to db manager")
PATH = "exchanges"
ARCHIVE = "old exchanges"


def make_table(date):
    date = date.lower()
    conn = sqlite3.connect(f"{PATH}/{date}.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE if not exists entries (
              user_id INT,
              entry_url STR)""")
    
def getExchanges() -> list:
    allexchanges = os.listdir(PATH)
    exchanges = []
    for i in allexchanges:
        exchanges.append(str(i).strip(".db"))
    return exchanges

def joinExchange(date, user_id, entry_url):
    date = date.lower()
    conn = sqlite3.connect(f"{PATH}/{date}.db")
    c = conn.cursor()

    c.execute(("""
            INSERT INTO entries VALUES (?,?)   
               """),(user_id,entry_url))
    conn.commit()
    conn.close() 

def archive(date):
    conn = sqlite3.connect(f"{PATH}/{date}.db")

    date = date.lower()
    conn.close()
    os.rename(src = f"{PATH}/{date}.db",dst = f"{ARCHIVE}/{date}.db")

def show_all(date):
    if os.path.exists(f"{PATH}/{date}.db"):
        conn = sqlite3.connect(f"{PATH}/{date}.db")
        c = conn.cursor()

        c.execute("SELECT * FROM entries")
        items = c.fetchall()
        return items

def whoJoined(date):
    users = []
    for row in show_all(date):
        users.append(row[0])
    return users
def userJoined(date, user_id):
    if user_id in whoJoined(date):
        return True
    else:
        return False
    
def shuffle(date):
    
    output = []
    usedLinks = []
    allrows = show_all(date)
    if len(allrows) < 2:
        return None
    usercount = allrows
    links = []
    for link in allrows:
        links.append(link[1])
    
    for user in allrows:
        
        choice = random.choice(links)
        while choice == user[1]:
            choice = random.choice(links)
        links.remove(choice)
        output.append((user[0],choice))
    return output
