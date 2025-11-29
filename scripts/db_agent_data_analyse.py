import sqlite3

def main():
    print("Seeing db agent data")
    conn = sqlite3.connect('db/db_agent_data.db')

    print("\nPrinting successful queries")
    cursor = conn.execute("""SELECT
        *
        FROM SUCCESSES
        LIMIT 5;"""
    )
    for row in cursor:
        print(row)

    print("\nPrinting failed queries")
    cursor = conn.execute("""SELECT
        *
        FROM FAILURES
        LIMIT 5;"""
    )
    for row in cursor:
        print(row)
    

if __name__=="__main__":
    main()