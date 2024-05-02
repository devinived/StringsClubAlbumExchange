import sqlite3
import os
from os import listdir
from os.path import isfile, join
import random
import asyncio
print("Connected to db manager")
CURRENT = "exchanges"
ARCHIVE = "old exchanges"


def make_table(date):
    date = date.lower()
    conn = sqlite3.connect(f"{CURRENT}/{date}.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE if not exists entries (
              user_id INT,
              entry_url STR,
              entry_name STR)""")
    
def getExchanges():
    allexchanges = os.listdir(CURRENT)
    exchanges = []
    for i in allexchanges:
        exchanges.append(str(i).strip(".db"))
    return exchanges

def joinExchange(date, user_id, entry_url, entry_name):
    date = date.lower()
    conn = sqlite3.connect(f"{CURRENT}/{date}.db")
    c = conn.cursor()

    c.execute(("""
            INSERT INTO entries VALUES (?,?,?)   
               """),(user_id,entry_url,entry_name))
    conn.commit()
    conn.close() 

def archive(date):
    date = date.lower()
    os.rename(src = f"{CURRENT}/{date}.db",dst = f"{ARCHIVE}/{date}.db")

def show_all(date):
    if os.path.exists(f"{CURRENT}/{date}.db"):
        conn = sqlite3.connect(f"{CURRENT}/{date}.db")
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
def getNameforAlbum(date, album_link):
    conn = sqlite3.connect(f"{CURRENT}/{date}.db")
    c = conn.cursor()
    c.execute("SELECT entry_name fROM entries WHERE entry_url = (?)", (album_link,))
    result = c.fetchone()
    return str(result).replace("[","").replace("(","").replace("]","").replace(")","").replace(",","")
def shuffle(date):
    redo = True
    while redo:
        redo = False
        output = []
        allrows = show_all(date)
        if len(allrows) < 2:
            return None
        usercount = allrows
        links = []
        for link in allrows:
            links.append(link[1])

        for user in allrows:
            if len(links) == 1 and user[1] in links:
                redo = True
                output=[]
                links=[]
            else:
                choice = random.choice(links)
                while choice == user[1]:
                    choice = random.choice(links)
                links.remove(choice)
                output.append((user[0],choice,getNameforAlbum(date,choice)))
        #this check here just in case for some reason the output doesnt have everyone's assignment, which has happened during testing
        if len(output) == len(allrows):
            return output
        else:
            redo=True
            output=[]
            links=[]