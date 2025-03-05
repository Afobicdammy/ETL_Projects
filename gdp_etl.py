"""
The URL:
'https://web.archive.org/web/20230902185326/https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'

The information needs to be available as a csv = Countries_by_GDP.csv
It also needs to be available as a databasefile = World_Economies.db that will be used to populate a table Countries_by_GDP in a database
Log files
"""


"""
"""

# Importing the neccessary libraries
import requests # to access the url 
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

# setting up the requirements

url = 'https://web.archive.org/web/20230902185326/https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
table_attribs = ['Country', 'GDP_USD_millions']
db_name = 'World_Economies.db'
table_name = 'Countries_by_GDP'
csv_path = './Countries_by_GDP.csv'


# Step1: Extract from the Url
"""
 - extract data from the web page using request.get() as text so .text() (1)
 - parse they text to an HTML object using beautifulsoup (2)
 - create an empty data frame with columns that will store the data (3)
 - extract all body attributes from the HTML object, then extract all rows from the body using the tr attribute (4)
 - validate the data in those rows (5)
 - store all this entries in a dictionary, then append the dictionary to the data frame (6)
"""

def extract(url, table_attribs):
    page = requests.get(url).text #(1)
    data = BeautifulSoup(page, 'html.parser') #(2)
    df = pd.DataFrame(data,columns=table_attribs) #(3)
    tables = data.find_all('tbody') #(4)
    rows = data.find_all('tr') #(4)

    for row in rows: 
        col = row.find_all('td')
        if len(col)!=0:
            if col[0].find('a') is not None and '—' not in col[2]:
                data_dict = {"Country": col[0].a.contents[0],
                             "GDP_USD_millions": col[2].contents[0]}
                df1 = pd.DataFrame(data_dict, index=[0])
                df = pd.concat([df,df1], ignore_index=True)
    return df

#Step2: Transform
"""
- convert content of the column GDP_USD_millions from int to float
- convert the values from millions to billions
- change column name from GDP_USD_millions to GDP_USD_billions
"""
def transform(df):
    GDP_list = df["GDP_USD_millions"].tolist()
    GDP_list = [float("".join(x.split(','))) for x in GDP_list]
    GDP_list = [np.round(x/1000,2) for x in GDP_list]
    df["GDP_USD_millions"] = GDP_list
    df=df.rename(columns = {"GDP_USD_millions":"GDP_USD_billions"})
    return df

#Step3: Load
"""
-
"""

def load_to_csv(df, csv_path):
    df.to_csv(csv_path)

def load_to_db(df, sql_connection, table_name):
     df.to_sql(table_name, sql_connection, if_exists='replace', index=False)
    

def log_progress(message):
    ''' This function logs the mentioned message at a given stage of the 
    code execution to a log file. Function returns nothing.'''
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now() # get current timestamp 
    timestamp = now.strftime(timestamp_format) 
    with open("./etl_project_log.txt","a") as f: 
        f.write(timestamp + ' : ' + message + '\n')  



url = 'https://web.archive.org/web/20230902185326/https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
table_attribs = ["Country", "GDP_USD_millions"]
db_name = 'World_Economies.db'
table_name = 'Countries_by_GDP'
csv_path = './Countries_by_GDP.csv'
log_progress('Preliminaries complete. Initiating ETL process')
df = extract(url, table_attribs)
log_progress('Data extraction complete. Initiating Transformation process')
df = transform(df)
log_progress('Data transformation complete. Initiating loading process')
load_to_csv(df, csv_path)
log_progress('Data saved to CSV file')
sql_connection = sqlite3.connect('World_Economies.db')
log_progress('SQL Connection initiated.')
load_to_db(df, sql_connection, table_name)
log_progress('Data loaded to Database as table. Running the query')
query_statement = f"SELECT * from {table_name} WHERE GDP_USD_billions >= 100"
run_query(query_statement, sql_connection)
log_progress('Process Complete.')
sql_connection.close()

