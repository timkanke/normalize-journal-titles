import click
import duckdb
import logging
import re

from pathlib import Path

from njt_isxn_utils import remove_non_issn, remove_non_isbn
from njt_requests import issn_lookup, isbn_lookup_lc

logger = logging.getLogger(__name__)

@click.command()
@click.argument('xlsx_file', type=click.Path(exists=True))
def normalize(xlsx_file):
    con = duckdb.connect(':memory:')

    # load file
    con.execute("CREATE TABLE report AS SELECT * FROM read_xlsx(?)", [xlsx_file])

    # Convert issn without hyphen to have one
    con.sql("UPDATE report SET ISSN = regexp_replace(ISSN, '(\\d{4})(\\d{4})', '\\1-\\2') WHERE LENGTH(ISSN) = 8")

    # load lookup_tables
    con.execute("CREATE TABLE IF NOT EXISTS book_list AS SELECT * FROM './data_lookup_tables/book_list_wikidata.csv'")
    # Need replace for first time using Wikidata data
    #con.sql("UPDATE book_list SET isbn13 = REPLACE(isbn13, '-', '')")
    #con.sql("UPDATE book_list SET isbn10 = REPLACE(isbn10, '-', '')")

    con.execute("CREATE TABLE IF NOT EXISTS journal_list AS SELECT * FROM './data_lookup_tables/journal_list_wikidata.csv'")

    # TODO Add isbn to join
    # Create working table joining wikidata list issn
    con.sql(f"CREATE TABLE working_table AS (SELECT * FROM report LEFT OUTER JOIN journal_list on report.ISSN = journal_list.issn AND report.ISSN = journal_list.issnl)")

    # Create a list of distinct ISSN column items
    issn_tuple = con.sql("SELECT DISTINCT ISSN FROM working_table WHERE issn IS NOT NULL AND issnl IS NULL").fetchall()
    issn_column = [item[0] for item in issn_tuple]
    logger.debug(issn_column)

    # Create issn_list from issn_column
    issn_list = remove_non_issn(issn_column)
    logger.debug(issn_list)

    # Lookup requests for title by issn
    issn_and_titles = issn_lookup(issn_list)
    logger.debug(issn_and_titles)
    if issn_and_titles:
        con.executemany("INSERT INTO journal_list (journalLabel, issn) VALUES (?, ?)", issn_and_titles)
    else:
        logger.info("Scraped journal list is empty.")

    # Create isbn_list from issn_column
    isbn_list = remove_non_isbn(issn_column)
    logger.debug(isbn_list)

    # Lookup requests for title by isbn
    isbn_and_titles = isbn_lookup_lc(isbn_list)
    logger.debug(isbn_and_titles)
    if isbn_and_titles:
        con.executemany("INSERT INTO book_list (bookLabel, isbn13, isbn10) VALUES (?, ?, ?)", isbn_and_titles)
    else:
        logger.info("Scraped book list is empty.")

    con.sql(f"CREATE TABLE list_table (NormalizedTitle VARCHAR, isxn VARCHAR, isxn_1 VARCHAR)")
    con.sql(f"INSERT INTO list_table (NormalizedTitle, isxn, isxn_1) SELECT journalLabel AS NormalizedTitle, issn AS isxn, issnl AS isxn_1 FROM journal_list")
    con.sql(f"INSERT INTO list_table (NormalizedTitle, isxn, isxn_1) SELECT bookLabel AS NormalizedTitle, isbn10 AS isxn, isbn13 AS isxn_1 FROM book_list")

    # Save file
    path = Path(xlsx_file)
    save_xlsx_file = path.parent / (path.stem + "_NORMALIZED" + path.suffix)
    con.sql(f"CREATE TABLE final_table AS (SELECT * FROM report LEFT OUTER JOIN list_table ON report.ISSN = list_table.isxn OR report.ISSN = list_table.isxn_1)")
    con.sql(f"COPY final_table TO '{save_xlsx_file}' WITH (FORMAT xlsx, HEADER true)")
    
    # Save look up tables to CSV
    con.sql(f"COPY journal_list TO'./data_lookup_tables/journal_list_wikidata.csv' (HEADER, DELIMITER ',')")
    con.sql(f"COPY book_list TO'./data_lookup_tables/book_list_wikidata.csv' (HEADER, DELIMITER ',')")


def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

    logger.info("Starting")
    normalize()


if __name__ == "__main__":
    main()