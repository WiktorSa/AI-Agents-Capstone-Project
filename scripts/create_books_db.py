import sqlite3
import os
import pandas as pd

def main():
    os.makedirs("db", exist_ok=True)
    if os.path.exists('db/books.db'):
        print("Removing old database")
        os.remove("db/books.db")

    print("Reading csv file")
    df = pd.read_csv("dataset/BooksDatasetClean.csv")
    df = df.drop("Publish Date (Month)", axis=1)
    df = df.dropna()
    df = df.reset_index(drop=True)
    df['Authors'] = df['Authors'].apply(lambda x: x.replace("By ", ""))
    df.columns = ["TITLE", "AUTHORS", "DESCRIPTION", "CATEGORY", "PUBLISHER", "PRICE", "PUBLISH_YEAR"]

    print("Creating BOOKS database")
    conn = sqlite3.connect('db/books.db')
    df.to_sql("BOOKS", conn, index=True)
    print("Database created\n")

    print("Database columns")
    cursor = conn.execute("PRAGMA table_info(BOOKS);")
    for row in cursor:
        print(row)
    
    print("\nDatabase sample row")
    cursor = conn.execute("SELECT * FROM BOOKS LIMIT 1;")
    for row in cursor:
        print(row)

    conn.close()
    print("\nWhole process completed successfully")
    

if __name__=="__main__":
    main()
