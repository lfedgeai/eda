#!/usr/bin/env python3

"""ReceiptQueryAgent

Interacts with receipts.db SQLite database to answer natural language queries about receipts.
Supported queries:
- Show me all receipts.
- What is the total amount spent (including tips)?
- What's the average tip given by each customer?
- List all customers who tipped more than $1.
- Which receipt has the highest price?
- What’s the smallest tip recorded?
- Show me all purchases by '<Customer Name>'.
- Which customers spent more than $20 in total?
- Calculate tip percentage for each receipt.
- How many receipts are there in the database?
"""

import sqlite3
import argparse
import re
import sys

def parse_query(query):
    # Normalize the query string
    original = query.strip()
    original = original.strip('"\' "').rstrip('.')
    q = original.lower()

    if 'show me all receipts' in q:
        sql = 'SELECT * FROM receipts'
    elif 'total amount spent' in q:
        sql = 'SELECT SUM(price + tip) AS total_spent FROM receipts'
    elif 'average tip' in q and 'customer' in q:
        sql = 'SELECT customer_name, AVG(tip) AS average_tip FROM receipts GROUP BY customer_name'
    elif (m := re.search(r'tipped more than \$?(\d+(?:\.\d+)?)', q)):
        x = m.group(1)
        sql = f'SELECT DISTINCT customer_name FROM receipts WHERE tip > {x}'
    elif 'highest price' in q:
        sql = 'SELECT * FROM receipts ORDER BY price DESC LIMIT 1'
    elif 'smallest tip' in q or 'min tip' in q:
        sql = 'SELECT MIN(tip) AS smallest_tip FROM receipts'
    elif 'purchases by' in q:
        m = re.search(r'purchases by\s+(.+)', original, re.IGNORECASE)
        if m:
            name = m.group(1).strip("'\" ")
            sql = f"SELECT * FROM receipts WHERE customer_name = '{name}'"
        else:
            sql = None
    elif 'customers spent more than' in q:
        m = re.search(r'customers spent more than \$?(\d+(?:\.\d+)?)', q)
        if m:
            x = m.group(1)
            sql = f'SELECT customer_name, SUM(price + tip) AS total_spent FROM receipts GROUP BY customer_name HAVING total_spent > {x}'
        else:
            sql = None
    elif 'tip percentage' in q:
        sql = 'SELECT receipt_id, customer_name, (tip / price) * 100.0 AS tip_percentage FROM receipts'
    elif 'how many receipts' in q or 'number of receipts' in q:
        sql = 'SELECT COUNT(*) AS receipt_count FROM receipts'
    else:
        sql = None
    return sql

def execute_query(db_path, sql):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [col[0] for col in cur.description]
    finally:
        conn.close()
    return rows, cols

def format_and_print(rows, columns):
    if not rows:
        print('No results found.')
        return
    # Single value
    if len(rows) == 1 and len(columns) == 1:
        print(rows[0][0])
        return
    # Header
    print('\t'.join(columns))
    for row in rows:
        print('\t'.join(str(row[col]) for col in columns))

def main():
    parser = argparse.ArgumentParser(description='ReceiptQueryAgent for querying receipts.db')
    parser.add_argument('query', nargs='*', help='Natural language query')
    parser.add_argument('--db', default='receipts.db', help='Path to SQLite database file')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    args = parser.parse_args()

    if args.interactive or not args.query:
        print("Entering interactive mode. Type 'exit' or 'quit' to leave.")
        while True:
            try:
                user_input = input('Query> ')
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if user_input.lower() in ('exit', 'quit'):
                break
            sql = parse_query(user_input)
            if not sql:
                print("Sorry, I couldn't understand that query.")
                continue
            try:
                rows, cols = execute_query(args.db, sql)
                format_and_print(rows, cols)
            except Exception as e:
                print(f'Error: {e}')
    else:
        query = ' '.join(args.query)
        sql = parse_query(query)
        if not sql:
            print("Sorry, I couldn't understand that query.")
            sys.exit(1)
        try:
            rows, cols = execute_query(args.db, sql)
            format_and_print(rows, cols)
        except Exception as e:
            print(f'Error: {e}')
            sys.exit(1)

if __name__ == '__main__':
    main()