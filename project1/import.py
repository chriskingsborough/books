import psycopg2
import csv

def main():
    """Main function to import data"""

    # first read csv into Memory
    with open('books.csv', 'r') as infile:
        # remove the first header line when creating data
        books = [tuple(i) for i in csv.reader(infile)][1:]

    conn = psycopg2.connect(
        host="ec2-54-163-245-44.compute-1.amazonaws.com",
        database="dbpeu4qdp8rf1b",
        user="wblnbsabtlpfnv",
        password="eb96c0a17e07f71630dfc1c6eb765e37092353bd07092084976abe0c7dc8d046"
    )

    insert_statement = """
    INSERT INTO BOOKS (isbn, title, author, year)
    VALUES (%s, %s, %s, %s)
    """

    cur = conn.cursor()
    cur.executemany(insert_statement, books)

    cur.close()
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
