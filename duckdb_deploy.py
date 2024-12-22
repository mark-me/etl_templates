import pathlib

import duckdb

def main():
    dir_scripts = "output/duckdb/"
    con = duckdb.connect("output/duckdb.db")

    files = [f for f in pathlib.Path().glob(dir_scripts + "*.sql")]
    print(files)

    for file in files:
        with open(file, 'r') as file:
            ddl_statement = file.read()
        con.sql(ddl_statement)

    con.close()

if __name__ == "__main__":
    main()
