from pathlib import Path

import duckdb

def main():
    dir_scripts = "output/duckdb/"
    con = duckdb.connect("output/duckdb/duckdb.db")

    files = sorted(Path().glob(dir_scripts + "*.sql"))

    for file in files:
        print("Executing: " + file.name)
        with open(file, 'r') as file:
            ddl_statement = file.read()
        con.sql(ddl_statement)

    con.close()

if __name__ == "__main__":
    main()
