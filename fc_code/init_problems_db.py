# FeatCode Implementation :: Init Table
# author: Scott Skibin

from featcode import *
import csv

# Initialize the data/problems.db database, create the PROBLEMS table and fill it with all of the LeetCode problems in data/default_urls.txt
fc = FeatCode()
fc.open_db_connection()
fc.create_table()
with open('data/default_urls.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    # count = 1
    for _, url in list(csv_reader)[1:]:
        # print(f'{count}) {url}')
        fc.add_problem(url) 
        # count += 1 
csv_file.close()
fc.close_db_connection()