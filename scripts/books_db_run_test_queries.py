import sqlite3

# Need to add upper everywhere to be case insensitive
def main():
    print("Testing a few queries")
    conn = sqlite3.connect('db/books.db')

    print("\nSearch for certain authors")
    cursor = conn.execute("""SELECT
        TITLE, AUTHORS
        FROM BOOKS
        WHERE UPPER(AUTHORS) LIKE UPPER('%martin cruz%') OR UPPER(AUTHORS) LIKE UPPER("%james d.%")
        LIMIT 5;"""
    )
    for row in cursor:
        print(row)

    print("\nExclude certain authors")
    cursor = conn.execute("""SELECT
        TITLE, AUTHORS
        FROM BOOKS
        WHERE UPPER(AUTHORS) NOT LIKE UPPER('%martin cruz%') AND UPPER(AUTHORS) NOT LIKE UPPER("%james d.%")
        LIMIT 5;"""
    )
    for row in cursor:
        print(row)

    print("\nSearch for keywords (that fit into categories)")
    cursor = conn.execute("""SELECT
        TITLE, AUTHORS, CATEGORY, DESCRIPTION
        FROM BOOKS
        WHERE UPPER(CATEGORY) LIKE UPPER('%autobiography%') OR UPPER(DESCRIPTION) LIKE UPPER("%autobiography%") 
        LIMIT 3;"""
    )
    for row in cursor:
        print(row)
        print()

    print("\nSearch for keywords (that fit into description)")
    cursor = conn.execute("""SELECT
        TITLE, AUTHORS, CATEGORY, DESCRIPTION
        FROM BOOKS
        WHERE UPPER(CATEGORY) LIKE UPPER('%corporation%') OR UPPER(DESCRIPTION) LIKE UPPER("%corporation%") 
        LIMIT 3;"""
    )
    for row in cursor:
        print(row)
        print()

    print("\nExclude keywords (that fit into categories)")
    cursor = conn.execute("""SELECT
        TITLE, AUTHORS, CATEGORY, DESCRIPTION
        FROM BOOKS
        WHERE UPPER(CATEGORY) NOT LIKE UPPER('%autobiography%') AND UPPER(DESCRIPTION) NOT LIKE UPPER("%autobiography%") 
        LIMIT 3;"""
    )
    for row in cursor:
        print(row)
        print()

    print("\nExclude keywords (that fit into description)")
    cursor = conn.execute("""SELECT
        TITLE, AUTHORS, CATEGORY, DESCRIPTION
        FROM BOOKS
        WHERE UPPER(CATEGORY) NOT LIKE UPPER('%corporation%') AND UPPER(DESCRIPTION) NOT LIKE UPPER("%corporation%") 
        LIMIT 3;"""
    )
    for row in cursor:
        print(row)
        print()
    

if __name__=="__main__":
    main()