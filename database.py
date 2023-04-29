import sqlite3
import pandas as pd


class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('BudgetAppDatabase.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS Expenditure (
                name text,
                amount real,
                frequency text,
                tag text,
                start_date text,
                end_date text
                )
            ''')
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS Income (
                name text,
                amount real,
                frequency text,
                tag text,
                start_date text,
                end_date text
                )
            ''')
        self.conn.commit()

    def delete_table(self, table):
        self.cursor.execute(f'''
            DROP TABLE {table}
            ''')
        self.conn.commit()

    def pull_all_from_table(self, table):
        self.cursor.execute(f'''
        SELECT rowid, * FROM {table}
        ''')
        return self.cursor.fetchall()

    def query(self, table, column, query_type, query):
        self.cursor.execute(f'''
        SELECT rowid, * FROM {table} WHERE {column} {query_type} '{query}'
        ''')
        return self.cursor.fetchall()

    def update(self, table, column, change, rowid):
        self.cursor.execute(f'''
        UPDATE {table} SET {column} = {change} WHERE rowid = '{rowid}'
        ''')
        self.conn.commit()
        return self.cursor.fetchall()

    def update_record(self, table, name, cost, frequency, tag, start_date, end_date, rowid):
        self.cursor.execute(f'''
        UPDATE {table} SET name = ?, amount = ?, frequency = ?, tag = ?, start_date = ?, end_date = ?
        WHERE rowid = ?
        ''', (name, cost, frequency, tag, start_date, end_date, rowid))
        self.conn.commit()
        return self.cursor.fetchall()

    def delete(self, table, column, query_type, query):
        self.cursor.execute(f'''
        DELETE from {table} WHERE {column} {query_type} '{query}'
        ''')
        self.conn.commit()
        return self.cursor.fetchall()

    def add_expenditure(self, expenditure_name, amount, frequency, tag, start_date, end_date):
        self.cursor.execute('''
            INSERT INTO Expenditure VALUES (?, ?, ?, ?, ?, ?)
        ''', (expenditure_name, amount, frequency, tag, start_date, end_date))
        self.conn.commit()

    def add_income(self, income_name, amount, frequency, tag, start_date, end_date):
        self.cursor.execute('''
            INSERT INTO Income VALUES (?, ?, ?, ?, ?, ?)
        ''', (income_name, amount, frequency, tag, start_date, end_date))
        self.conn.commit()

    def order_table_by(self, table, column, ascending):
        if ascending:
            ascending = ''
        else:
            ascending = 'DESC'
        self.cursor.execute(f'''
        SELECT rowid, * FROM {table} ORDER BY {column} {ascending}
        ''')
        return self.cursor.fetchall()

    def get_info(self, table):
        self.cursor.execute(f'''
        PRAGMA table_info({table})
        ''')
        return self.cursor.fetchall()

    def get_columns(self, table):
        columns = [column[1] for column in self.get_info(table)]
        columns.insert(0, 'rowid')
        return columns

    def return_df(self, table):
        columns = self.get_columns(table)
        info = db.pull_all_from_table(table)
        df = pd.DataFrame(info, columns=columns)
        df.set_index('rowid', inplace=True)
        return df

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    db = Database()
    db.delete_table('Expenditure')
    db.delete_table('Income')
    db.close()
