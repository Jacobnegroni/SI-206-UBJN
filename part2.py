import unittest
import sqlite3
import json
import os

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

cur, conn = setUpDatabase('project.db')

# Find years
def find_years(cur):
    cur.execute("SELECT year FROM Population")
    years_set = set(cur.fetchall())
    years = []
    for element in years_set:
    	years = years + [element[0]]
    years.sort(reverse = True)
    return years

# Total population for each year
def find_total_population(cur, years):
    total_population = {}
    for year in years:
    	population_sum = 0
    	cur.execute("SELECT population FROM Population WHERE year=?",(year,))
    	for element in cur.fetchall():
    		population_sum += element[0]
    	total_population[year] = population_sum
    return total_population


# Total people in poverty for each year
def find_total_poverty(cur, years):
    total_poverty = {}
    for year in years:
    	poverty_sum = 0
    	cur.execute("SELECT population,poverty_rate FROM Population JOIN Poverty ON Population.id=Poverty.id WHERE Population.year=?",(year,))
    	for element in cur.fetchall():
    		poverty_sum += round(element[0]*element[1])
    	total_poverty[year] = poverty_sum
    return total_poverty
# Write results to file
def write_results(years, total_population, total_poverty):
    file = open('results.txt','w')
    file.write('USA population stats\nYear\tPopulation\tIn poverty\n')
    for year in years:
    	file.write(str(year)+'\t'+str(total_population[year])+'\t'+str(total_poverty[year])+'\n')
    file.close()

cur, conn = setUpDatabase('project.db')
years = find_years(cur)
total_population = find_total_population(cur, years)
total_poverty = find_total_poverty(cur, years)
write_results(years, total_population, total_poverty)