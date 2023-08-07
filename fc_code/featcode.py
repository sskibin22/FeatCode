import sqlite3
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class FeatCode:
    def __init__(self):
        self.__conn = None
        self.__cursor = None
        
    def open_db_connection(self):
        self.__conn = sqlite3.connect('data/problems.db')
        self.__cursor = self.__conn.cursor()
        
    def close_db_connection(self):
        self.__cursor.close()
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
                SEEN        INTEGER                               NOT NULL,
                USOL        TEXT);''')
        else:
            print('Table "PROBLEMS" already exists in database.')

    def add_col(self, col_name : str):
        self.__cursor.execute(f'''ALTER TABLE PROBLEMS ADD COLUMN {col_name} TEXT;''')
        self.__conn.commit()
            
    def add_problem(self, url: str) -> tuple[int, str]:
        url_exists = bool(self.__cursor.execute('''SELECT count(*) FROM PROBLEMS WHERE URL = ?;''',(url,)).fetchone()[0])
        if url_exists:
            print("Problem already exists in table.")
            return (0, None)
    
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument("--log-level=3")
            driver = webdriver.Chrome(options=options)
            driver.get(url)

            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "_1l1MA"))) 

            html = driver.page_source
            soup = bs4.BeautifulSoup(html, "html.parser")

            title = url.split('/')[-2].replace('-', ' ').title()
            title_html = f'<div id="title"><strong>{title}</strong></div>\n' 
            description_html = str(soup.find("div", {"class": "_1l1MA"}))
            
            replace = ['<code>', '</code>']
            for rep in replace:
                description_html = description_html.replace(rep, '')
                    
            problem_description = title_html + description_html
            
        except:
            print('ERROR: invalid URL')
            driver.quit()
            return (-1, None)
            
        else:
            self.__conn.execute('''INSERT INTO PROBLEMS (TITLE,URL,PROMPT,SEEN) VALUES(?,?,?,0)''', (title, url, problem_description)) 
            self.__conn.commit()
            driver.quit()
            return (1, title)
        
    def remove_problem(self, title : str) -> int:
        table_empty = self.__cursor.execute("SELECT count(*) FROM PROBLEMS;").fetchone()[0] <= 0
        if table_empty:
            print('Table is empty.')
            return 0
        
        prob_exists = bool(self.__cursor.execute('''SELECT count(*) FROM PROBLEMS WHERE TITLE = ?;''',(title,)).fetchone()[0])
        if not prob_exists:
            print("Problem does not exist in table.")
            return -1
        
        self.__cursor.execute('''DELETE FROM PROBLEMS WHERE TITLE = ?''',(title,))
        self.__conn.commit()
        return 1
    
    def mark_problem_as_seen(self, title: str):
        self.__cursor.execute('''UPDATE PROBLEMS SET SEEN = 1 WHERE TITLE = ?;''',(title,))
        self.__conn.commit()
        
    def mark_problem_as_unseen(self, title: str):
        self.__cursor.execute('''UPDATE PROBLEMS SET SEEN = 0 WHERE TITLE = ?;''',(title,))
        self.__conn.commit()

    def get_table(self):
        return self.__cursor.execute('''SELECT * FROM PROBLEMS;''').fetchall()
    
    def get_all_seen_problems(self):
        seen = self.__cursor.execute('''SELECT * FROM PROBLEMS WHERE SEEN = 1;''').fetchall()
        return [row[0] for row in seen]
    
    def get_all_unseen_problems(self):
        unseen = self.__cursor.execute('''SELECT * FROM PROBLEMS WHERE SEEN = 0;''').fetchall()
        return [row[0] for row in unseen]
    
    def get_problem_by_title(self, title: str):
        problem = self.__cursor.execute('''SELECT * FROM PROBLEMS WHERE TITLE = ?;''',(title,)).fetchone()
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
            print('-------------------------------------------------')
            if problem[5]:
                print(f'USOL: {problem[5]}')
            else:
                print(f'USOL: None')
            print('=================================================')
        else:
            print("Problem does not exist in table.")

        return problem

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
            print('-------------------------------------------------')
            if problem[5]:
                print(f'USOL: {problem[5]}')
            else:
                print(f'USOL: None')
            print('=================================================')
        return problem