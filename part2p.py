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
#The function takes a cursor and selects the ‘year’ field from the Population table. The entries in 
#rows are returned as a list of tuples and converted to a set to retain only unique elements. A list 
#of the years that was considered in the data is returned in descending order.
def find_years(cur):
	cur.execute("SELECT year FROM Population")
	years_set = set(cur.fetchall())
	years = []
	for element in years_set:
		years = years + [element[0]]
	years.sort(reverse = True)
	return years

# Total population for each year
#The function loops through each year in the list and the SQL Query selects the population 
#field of the row only where the year is the same as the year considered within the loop.  
#the population of each state for that particular year is summed up in a dummy variable population_sum 
#that is initiated at 0 for every loop. The total sum across all states is then appended as a value in the 
#dictionary (total_population) with the corresponding year as its key. 

def find_total_population(cur,years):
	total_population = {}
	for year in years:
		population_sum = 0
		cur.execute("SELECT population FROM Population WHERE year=?",(year,))
		for element in cur.fetchall():
			population_sum += element[0]
		total_population[year] = population_sum
	return total_population


# Total people in poverty for each year
#The function takes loops through each year in the years list. For each year, the  tables Population 
#and Poverty are joined using the ‘id’ column and only the entries which have the same year as the year 
#considered in the loop are filtered and fetched.  The two columns that are fetched are population from 
#the Population table and poverty_rate from the Poverty table.  The total population in poverty for each 
#state is then calculated by multiplying the poverty rate for that state by the state’s population and rounding 
#it to an integer. The total population in poverty all through the USA for that particular year is appended to the 
#dictionary as a value with the year as its key and the dictionary (total_poverty) is returned.
def find_total_poverty(cur,years):
	total_poverty = {}
	for year in years:
		poverty_sum = 0
		cur.execute("SELECT population,poverty_rate FROM Population \
			JOIN Poverty ON Population.id=Poverty.id WHERE Population.year=?",(year,))
		for element in cur.fetchall():
			poverty_sum += round(element[0]*element[1])
		total_poverty[year] = poverty_sum
	return total_poverty


# Write results to file
#The function opens a text file in write format and writes an introductory line and header in the file. The header 
#consists of 3 columns, the year, total population and the total population in poverty. Each year is looped through 
#from the list years. The corresponding total population is retrieved from the total_population dictionary and the corresponding 
#population in poverty is retrieved using the total_poverty dictionary. Each entry is written in the text file and 
#then the file closes and the function terminates.
def write_results(years,total_population,total_poverty):
	file = open('results.txt','w')
	file.write('USA population stats\nYear\tPopulation\tIn poverty\n')
	for year in years:
		file.write(str(year)+'\t'+str(total_population[year])+'\t'+str(total_poverty[year])+'\n')
	file.close()

cur, conn = setUpDatabase('project.db')
years = find_years(cur)
total_population = find_total_population(cur,years)
total_poverty = find_total_poverty(cur,years)
write_results(years,total_population,total_poverty)
