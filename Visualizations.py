import requests
import os
import json
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
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

def bar_plotter(ax, x, y, x_label, y_label, title, color):
    fonts = 40
    ax.set_title(title, fontsize=fonts)
    ax.bar(x, y, color=color, width=0.4)
    ax.set_xlabel(x_label, fontsize=fonts)
    ax.set_xticklabels(x, rotation=25)
    ax.set_ylabel(y_label, fontsize=fonts)
    ax.tick_params(labelsize=fonts)


def visualizations(db_name):
    cur, conn = setUpDatabase('project.db')
    cur.execute('select year from population group by year')
    years = []
    for years_list in cur.fetchall():
        years.append(years_list[0])
    avg_pov = []
    for year in years:
        query = ("select po.poverty_rate "
                 "from Population as p Join poverty as po on p.id = po.id "
                 "where p.year = ?"
                 " GROUP BY p.state")
        cur.execute(query, (year,))
        for pov in cur.fetchall():
            temp = [item for item in pov]
        avg_pov.append(sum(temp)/len(temp))
    x_years = [str(i) for i in years]

    fig, ax = plt.subplots(3, figsize=(25, 25), constrained_layout=True)
    
    #Visualization 1
    axis = ax[0]
    x = x_years
    y = avg_pov
    title = 'Average US Poverty Rate '
    xlabel = 'Year'
    ylabel = 'Average Poverty Rate'
    color = 'g'
    bar_plotter(axis, x, y, xlabel, ylabel, title, color)

    cur.execute('select p.state,po.poverty_rate from Population as p Join poverty as po on p.id = po.id where p.year = 2019 order by poverty_rate desc')
    state_pov_dict = {}
    for item in cur.fetchall():
        state_pov_dict[item[0]] = item[1]
    x_states = list(state_pov_dict.keys())[:10]
    y_pov_rate = [state_pov_dict[keys] for keys in x_states]
    
    #Visualization 2
    axis = ax[1]
    x = x_states
    y = y_pov_rate
    title = 'Top 10 States With Highest Poverty Rate In 2019'
    xlabel = 'State'
    ylabel = 'Poverty Rate In 2019'
    color = 'r'
    bar_plotter(axis, x, y, xlabel, ylabel, title, color)

    growth_rate_dict = {}
    query = 'select p.population from Population as p Join poverty as po on p.id = po.id where (p.year = ? and p.state = ?)'
    for state in x_states:
        y1 = '2018'
        cur.execute(
            query, (y1, state))
        pop1 = cur.fetchall()
        y2 = '2019'
        cur.execute(
            query, (y2, state))
        pop2 = cur.fetchall()
        growth_rate_dict[state] = ((pop2[0][0] - pop1[0][0])/pop1[0][0])*100
    print(growth_rate_dict)

    #Visualization 3
    axis = ax[2]
    x = x_states
    y = growth_rate_dict.values()
    title = 'Population Growth Rate of 10 Poorest States (Year 2018/19)'
    xlabel = 'State'
    ylabel = 'Growth Rate'
    color = 'b'
    bar_plotter(axis, x, y, xlabel, ylabel, title, color)


visualizations('project.db')
