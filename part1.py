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
# The function looks at the current path and sets up the database. A connection is made to the database using the connect() method and a cursor object is defined. 


def getdataAPI(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content,'html.parser')
    data = json.loads(soup.text)
    return data['data']
# The function takes a url string and uses the get() method from requests module to retrieve the webpage. Content parsing using BeautifulSoup. The json module loads() method is used to convert the text into a list of dictionaries.

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
#  Creates the Table Population in the project.db database if it does not exist. Each dictionary in the list contains the keys (ID State, Year, State,P opulation). If the new total number of rows equals the nrows+limit number, the for loop is exited by using the break command. Changes are committed.
# Parameters:
# 	data_json (list of dict) Dictionary containing the data
# 	cur (SQL obj) Cursor for the database
# 	conn(SQL Obj) Connection to the database
# limit (int) limit for the number of new entries added to the table. value is 20


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

# Creates the table for poverty data.  Very similar to setUpPopulationTable() function but instead of the population field, the ‘poverty rate’ is considered. Existing entries are ignored, new entries are added and the for loop is exited using the break command. Changes are committed.
# Database
cur, conn = setUpDatabase('project.db')

data1 = getdataAPI('https://datausa.io/api/data?drilldowns=State&measures=Population')
setUpPopulationTable(data1, cur, conn)

data2 = getdataAPI('https://datausa.io/api/data?drilldowns=State&measures=Poverty%20Rate')
setUpPovertyTable(data2, cur, conn)
