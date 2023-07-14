import sqlite3
import pandas as pd
import datetime

class DBStorage():
    def __init__(self):
        self.con = sqlite3.connect('links.db')
        self.setup_tables()

    def setup_tables(self):
        cur = self.con.cursor()
        results_table = r"""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                query TEXT,
                rank INTEGER,
                link TEXT,
                title TEXT,
                snippet TEXT,
                html TEXT,
                created DATETIME,
                search_count INTEGER DEFAULT 1,
                UNIQUE(query, link)
            );
            """
        cur.execute(results_table)
        self.con.commit()
        cur.close()

    def query_results(self, query):
        df = pd.read_sql(f"select * from results where query='{query}' order by rank asc", self.con)
        return df

    def insert_row(self, values):
        cur = self.con.cursor()
        try:
            cur.execute('INSERT INTO results (query, rank, link, title, snippet, html, created) VALUES(?, ?, ?, ?, ?, ?, ?)', values)
            self.con.commit()
        except sqlite3.IntegrityError:
            pass
        cur.close()

    def update_row(self, query):
        cur = self.con.cursor()
        try:
            cur.execute(f"UPDATE results SET search_count = search_count + 1 WHERE query = '{query}'")
            self.con.commit()
        except sqlite3.IntegrityError:
            pass
        cur.close()

    def top_queries_this_month(self):
        cur = self.con.cursor()
        current_month = datetime.datetime.now().strftime("%Y-%m")
        query = f"""
            SELECT DISTINCT query, search_count
            FROM results
            WHERE strftime('%Y-%m', created) = '{current_month}'
            ORDER BY search_count DESC
            LIMIT 10
        """
        cur.execute(query)
        top_queries = cur.fetchall()
        cur.close()
        return top_queries
    
    def get_autocomplete_suggestions(self, query):
        cur = self.con.cursor()
        cur.execute(f"SELECT DISTINCT query FROM results WHERE query LIKE '{query}%' LIMIT 10")
        suggestions = [row[0] for row in cur.fetchall()]
        cur.close()
        return suggestions