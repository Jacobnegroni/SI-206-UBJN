import requests
import os
import json
from bs4 import BeautifulSoup
import sqlite3

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def getdataAPI(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content,'html.parser')
    data = json.loads(soup.text)
    return data['data']

def setUpPopulationTable(data_json, cur, conn, limit=20):
    cur.execute("CREATE TABLE IF NOT EXISTS Population (id TEXT PRIMARY KEY, year INTEGER, state TEXT, population INTEGER)")
    cur.execute("SELECT * FROM Population")
    nrows = len(cur.fetchall())
    for data in data_json:
        state_id = data['ID State'][5:]
        year = data['Year']
        key = state_id+'_'+year
        state = data['State']
        population = data['Population']
        cur.execute("INSERT OR IGNORE INTO Population (id, year, state, population) VALUES (?,?,?,?)",(key, year, state, population))
        cur.execute("SELECT * FROM Population")
        nrows_curr = len(cur.fetchall())
        if(nrows_curr == nrows+limit):
            break
    cur.execute("SELECT * FROM Population")
    nrows = len(cur.fetchall())
    conn.commit()
    print(str(nrows)+"/364 entries in the Population table")

def setUpPovertyTable(data_json, cur, conn, limit=20):
    cur.execute("CREATE TABLE IF NOT EXISTS Poverty (id TEXT PRIMARY KEY, year INTEGER, state TEXT, poverty_rate INTEGER)")
    cur.execute("SELECT * FROM Poverty")
    nrows = len(cur.fetchall())
    for data in data_json:
        state_id = data['ID State'][5:]
        year = data['Year']
        key = state_id+'_'+year
        state = data['State']
        poverty_rate = data['Poverty Rate']
        cur.execute("INSERT OR IGNORE INTO Poverty (id, year, state, poverty_rate) VALUES (?,?,?,?)",(key, year, state, poverty_rate))
        cur.execute("SELECT * FROM Poverty")
        nrows_curr = len(cur.fetchall())
        if(nrows_curr == nrows+limit):
            break
    cur.execute("SELECT * FROM Poverty")
    nrows = len(cur.fetchall())
    conn.commit()
    print(str(nrows)+"/364 entries in the Poverty table")


# Database
cur, conn = setUpDatabase('project.db')

data1 = getdataAPI('https://datausa.io/api/data?drilldowns=State&measures=Population')
setUpPopulationTable(data1, cur, conn)

data2 = getdataAPI('https://datausa.io/api/data?drilldowns=State&measures=Poverty%20Rate')
setUpPovertyTable(data2, cur, conn)
