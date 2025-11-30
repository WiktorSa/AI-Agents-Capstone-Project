import sqlite3
import os
import pandas as pd
import numpy as np

def main():
    print("Reading csv file\n")
    df = pd.read_csv("dataset/BooksDatasetClean.csv")
    df = df.drop("Publish Date (Month)", axis=1)
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.columns = ["TITLE", "AUTHORS", "DESCRIPTION", "CATEGORY", "PUBLISHER", "PRICE", "PUBLISH_YEAR"]

    print("5 random titles")
    data = np.random.choice(df['TITLE'].unique(), 5)
    for i, row in enumerate(data, 1):
        print(f'{i}: {row}')

    print("\n5 random authors")
    data = np.random.choice(df['AUTHORS'].unique(), 5)
    for i, row in enumerate(data, 1):
        print(f'{i}: {row}')

    print("\n5 random descriptions")
    data = np.random.choice(df['DESCRIPTION'].unique(), 5)
    for i, row in enumerate(data, 1):
        print(f'{i}: {row}')

    print("\5 random categories")
    data = np.random.choice(df['CATEGORY'].unique(), 5)
    for i, row in enumerate(data, 1):
        print(f'{i}: {row}')

    print("\n5 random publishers")
    data = np.random.choice(df['PUBLISHER'].unique(), 5)
    for i, row in enumerate(data, 1):
        print(f'{i}: {row}')

    print("\n5 random prices")
    data = np.random.choice(df['PRICE'].unique(), 5)
    for i, row in enumerate(data, 1):
        print(f'{i}: {row}')

    print("\n5 random publication years")
    data = np.random.choice(df['PUBLISH_YEAR'].unique(), 5)
    for i, row in enumerate(data, 1):
        print(f'{i}: {row}')

    print("\n5 random books")
    data = df.sample(5)
    for i, row in enumerate(data.iterrows(), 1):
        print(f'{i}: {row}')
    

if __name__=="__main__":
    main()