# FeatCode API :: FeatCode()
# author: Scott Skibin

# Import libraries
import sqlite3
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# The FeatCode class is an API intended for use with the FCGUI class in fc_gui/layout.py
# It utilizes the sqlite3 library to communicate with the problems database which is an SQLite .db file
class FeatCode:
    def __init__(self):
        self.__conn = None # connects to the problems database
        self.__cursor = None # cursor for interacting with the problems database
    
    # Opens a connection to the problems database
    def open_db_connection(self):
        self.__conn = sqlite3.connect('data/problems.db')
        self.__cursor = self.__conn.cursor()
    
    # Closes a connection with the problems database
    def close_db_connection(self):
        self.__cursor.close()
        self.__conn.close()
    
    # Creates the PROBLEMS table which will reside in data/problems.db
    def create_table(self):
        table_exists = self.__cursor.execute("""SELECT name 
                                                FROM sqlite_master 
                                                WHERE type='table'
                                                AND name='PROBLEMS'; """).fetchall()
        if not table_exists:
            self.__conn.execute('''CREATE TABLE PROBLEMS
                (ID         INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
                TITLE       TEXT                                  NOT NULL,
                URL         TEXT                                  NOT NULL,
                PROMPT      TEXT                                  NOT NULL,
                SEEN        INTEGER                               NOT NULL,
                USOL        TEXT
                TIME        TEXT);''')
        else:
            print('Table "PROBLEMS" already exists in database.')

    # Adds a column to the PROBLEMS table
    def add_col(self, col_name : str, type : str):
        self.__cursor.execute(f'''ALTER TABLE PROBLEMS ADD COLUMN {col_name} {type};''')
        self.__conn.commit()
    
    # Uses the selenium library to scrape a LeetCode problem's description and title form the given url
    # and then adds the scraped data to the PROBLEMS table as a new row.
    # Error code 0 is returned if the url already exists in the PROBLEMS database
    # Error code -1 is returned if the url is not a valid LeetCode problem url
    # 1 is returned along with the title of the problem if this method is a success
    def add_problem(self, url: str) -> tuple[int, str]:
        # Check if the url exists in the PROBLEMS table
        url_exists = bool(self.__cursor.execute('''SELECT count(*) FROM PROBLEMS WHERE URL = ?;''',(url,)).fetchone()[0])
        if url_exists:
            # print("Problem already exists in table.")
            return (0, None)

        # Try to find the problem description of a given leetcode using selenium and bs4
        # If something goes wrong return error code -1
        # Else insert the newly aquired LeetCode problem data into the PROBLEMS table and return 1u
        try:
            # Setup selenium webdriver options
            options = Options()
            options.add_argument('--headless')
            options.add_argument("--log-level=3")
            driver = webdriver.Chrome(options=options)

            # Get locate the url within the Chrome driver
            driver.get(url)

            # <div class = '_1l1MA'> is the div tag associated with the problem description html for a LeetCode problem
            # the selenium Chrome driver is used to search through the html source code as well as any java dependent html in order to find this div tag
            # WebDriverWait waits 30 seconds or until the given class name is found before it terminates
            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "_1l1MA"))) 

            # bs4 is used to parse the html file that was found with the '_1l1MA' class name in it
            html = driver.page_source
            soup = bs4.BeautifulSoup(html, "html.parser")

            # The title of the problem is obtained from the given url string and then built into an html div 'title' tag
            title = url.split('/')[-2].replace('-', ' ').title()
            title_html = f'<div id="title"><strong>{title}</strong></div>\n'

            # The description html is then scraped from the html file found using selenium
            description_html = str(soup.find("div", {"class": "_1l1MA"}))
            
            # The description html is then parsed for any <code> or </code> tags in order to remove them (they do not play nice with the HTMLLabel class)
            replace = ['<code>', '</code>']
            for rep in replace:
                description_html = description_html.replace(rep, '')
            
            # The new title html string is then prepended to the description html that was scraped with bs4
            problem_description = title_html + description_html
            
        except:
            # print('ERROR: invalid URL')
            driver.quit()
            return (-1, None)
            
        else:
            # Insert the title, (passed) url, and scraped decription html as strings into the PROBLEMS table
            self.__conn.execute('''INSERT INTO PROBLEMS (TITLE,URL,PROMPT,SEEN) VALUES(?,?,?,0)''', (title, url, problem_description)) 
            self.__conn.commit()
            driver.quit()
            return (1, title)
    
    # Removes a problem from given problem from the PROBLEMS table
    # Error code 0 is returned if the table is empty and nothing can be removed from it
    # Error code -1 is returned if the problem being removed does not exist (this is not necessary given the design of the GUI)
    def remove_problem(self, title : str) -> int:
        table_empty = self.__cursor.execute("SELECT count(*) FROM PROBLEMS;").fetchone()[0] <= 0
        if table_empty:
            # print('Table is empty.')
            return 0
        
        prob_exists = bool(self.__cursor.execute('''SELECT count(*) FROM PROBLEMS WHERE TITLE = ?;''',(title,)).fetchone()[0])
        if not prob_exists:
            # print("Problem does not exist in table.")
            return -1
        
        self.__cursor.execute('''DELETE FROM PROBLEMS WHERE TITLE = ?''',(title,))
        self.__conn.commit()
        return 1
    
    # Set a given problems SEEN variable to 1 in the PROBLEMS table
    def mark_problem_as_seen(self, title: str):
        self.__cursor.execute('''UPDATE PROBLEMS SET SEEN = 1 WHERE TITLE = ?;''',(title,))
        self.__conn.commit()
    
    # Set a given problems SEEN variable to 0 in the PROBLEMS table
    def mark_problem_as_unseen(self, title: str):
        self.__cursor.execute('''UPDATE PROBLEMS SET SEEN = 0 WHERE TITLE = ?;''',(title,))
        self.__conn.commit()

    # Save a given problems user input solution to the PROBLEMS table
    def save_solution(self, solution: str, pid: int):
        self.__cursor.execute('''UPDATE PROBLEMS SET USOL = ? WHERE ID = ?;''',(solution, pid,))
        self.__conn.commit()
    
    # Save a given problems time to the PROBLEMS table
    def save_time(self, time : str, pid: int):
        self.__cursor.execute('''UPDATE PROBLEMS SET TIME = ? WHERE ID = ?;''',(time, pid,))
        self.__conn.commit()

    # Return all items in the PROBLEMS table
    def get_table(self):
        return self.__cursor.execute('''SELECT * FROM PROBLEMS;''').fetchall()
    
    # Return a list of all problem ids marked as 'seen' (SEEN == 1)
    def get_all_seen_problems(self):
        seen = self.__cursor.execute('''SELECT * FROM PROBLEMS WHERE SEEN = 1;''').fetchall()
        return [row[0] for row in seen]
    
    # Return a list of all problem ids marked as 'unseen' (SEEN == 0)
    def get_all_unseen_problems(self):
        unseen = self.__cursor.execute('''SELECT * FROM PROBLEMS WHERE SEEN = 0;''').fetchall()
        return [row[0] for row in unseen]
    
    # Return a problem's data from the PROBLEMS table given it's title
    def get_problem_by_title(self, title: str):
        problem = self.__cursor.execute('''SELECT * FROM PROBLEMS WHERE TITLE = ?;''',(title,)).fetchone()
        # if problem:
        #     print('=================================================')
        #     print(f'ID: {problem[0]}')
        #     print('-------------------------------------------------')
        #     print(f'TITLE: {problem[1]}')
        #     print('-------------------------------------------------')
        #     print(f'URL: {problem[2]}')
        #     print('-------------------------------------------------')
        #     print(f'SEEN: {"TRUE" if problem[4] > 0 else "FALSE"}')
        #     print('-------------------------------------------------')
        #     print(f'PROMPT: {problem[3]}')
        #     print('-------------------------------------------------')
        #     if problem[5]:
        #         print(f'USOL: {problem[5]}')
        #     else:
        #         print(f'USOL: None')
        #     print('-------------------------------------------------')
        #     if problem[6]:
        #         print(f'TIME: {problem[6]}')
        #     else:
        #         print(f'TIME: 00:00:00')
        #     print('=================================================')
        # else:
        #     print("Problem does not exist in table.")
        return problem
    
    # Return a randomly selected problem and it's data from the PROBLEMS table
    def get_random_problem(self):
        problem = self.__cursor.execute('''SELECT * FROM PROBLEMS WHERE SEEN == 0 ORDER BY RANDOM() LIMIT 1;''').fetchone()
        # if problem:
        #     print('=================================================')
        #     print(f'ID: {problem[0]}')
        #     print('-------------------------------------------------')
        #     print(f'TITLE: {problem[1]}')
        #     print('-------------------------------------------------')
        #     print(f'URL: {problem[2]}')
        #     print('-------------------------------------------------')
        #     print(f'SEEN: {"TRUE" if problem[4] > 0 else "FALSE"}')
        #     print('-------------------------------------------------')
        #     print(f'PROMPT: {problem[3]}')
        #     print('-------------------------------------------------')
        #     if problem[5]:
        #         print(f'USOL: {problem[5]}')
        #     else:
        #         print(f'USOL: None')
        #     print('-------------------------------------------------')
        #     if problem[6]:
        #         print(f'TIME: {problem[6]}')
        #     else:
        #         print(f'TIME: 00:00:00')
        #     print('=================================================')
        return problem