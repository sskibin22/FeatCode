import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

class FeatCode:
    def __init__(self):
        self.__conn = None
        self.__cursor = None
    def open_db_connection(self):
        self.__conn = sqlite3.connect('data/problems.db')
        self.__cursor = self.__conn.cursor()
    def close_db_connection(self):
        self.__conn.close()
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
                SEEN        INTEGER                               NOT NULL);''')
        else:
            print('Table "PROBLEMS" already exists in database.')
            
    def add_problem(self, url: str):
        url_exists = bool(self.__cursor.execute('''SELECT count(*) FROM PROBLEMS WHERE URL = ?;''',(url,)).fetchone()[0])
        if url_exists:
            print("Problem already exists in table.")
            return
        browser = webdriver.Chrome()
        browser.get(url)
        browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        sleep(5)
        problem_description = browser.find_element(By.CLASS_NAME, "_1l1MA")
        title = url.split('/')[-2].replace('-', ' ')
        self.__conn.execute('''INSERT INTO PROBLEMS (TITLE,URL,PROMPT,SEEN) VALUES(?,?,?,0)''', (title, url, problem_description.text)) 
        self.__conn.commit()
        
    def remove_problem(self, id: int):
        table_empty = self.__cursor.execute("SELECT count(*) FROM PROBLEMS;").fetchone()[0] <= 0
        if table_empty:
            print('Table is empty.')
            return
        
        id_exists = bool(self.__cursor.execute('''SELECT count(*) FROM PROBLEMS WHERE ID = ?;''',(id,)).fetchone()[0])
        if not id_exists:
            print("Problem does not exist in table.")
            return
        
        self.__cursor.execute('''DELETE FROM PROBLEMS WHERE ID = ?''',(id,))
        self.__conn.commit()
    
    def get_problem_by_id(self, id: int):
        problem = self.__cursor.execute('''SELECT * FROM PROBLEMS WHERE ID = ?;''',(id,)).fetchone()
        if problem:
            print('=================================================')
            print(f'ID: {problem[0]}')
            print('-------------------------------------------------')
            print(f'TITLE: {problem[1]}')
            print('-------------------------------------------------')
            print(f'URL: {problem[2]}')
            print('-------------------------------------------------')
            print(f'SEEN: {"TRUE" if problem[4] > 0 else "FALSE"}')
            print('-------------------------------------------------')
            print(f'PROMPT: {problem[3]}')
            print('=================================================')
        else:
            print("Problem does not exist in table.")

    def get_random_problem(self):
        problem = self.__cursor.execute('''SELECT * FROM PROBLEMS WHERE SEEN == 0 ORDER BY RANDOM() LIMIT 1;''').fetchone()
        if problem:
            print('=================================================')
            print(f'ID: {problem[0]}')
            print('-------------------------------------------------')
            print(f'TITLE: {problem[1]}')
            print('-------------------------------------------------')
            print(f'URL: {problem[2]}')
            print('-------------------------------------------------')
            print(f'SEEN: {"TRUE" if problem[4] > 0 else "FALSE"}')
            print('-------------------------------------------------')
            print(f'PROMPT: {problem[3]}')
            print('=================================================')