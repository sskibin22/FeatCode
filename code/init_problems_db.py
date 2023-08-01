from featcode import *
import csv

fc = FeatCode()
fc.open_db_connection()
fc.create_table()
with open('data/default_urls.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for _, url in list(csv_reader)[1:]:
        fc.add_problem(url)  
csv_file.close()
fc.close_db_connection()