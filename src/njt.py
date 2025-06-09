import click
import duckdb
import logging
import re

from pathlib import Path

from njt_isxn_utils import remove_non_issn, remove_non_isbn
from njt_requests import issn_lookup, isbn_lookup

logger = logging.getLogger(__name__)

@click.command()
@click.argument('xlsx_file', type=click.Path(exists=True))
def normalize(xlsx_file):
    # TODO Change to persitent storage when adding comparing lists feature.
    con = duckdb.connect(':memory:')

    # Create isxn_lookup table
    con.execute("CREATE TABLE IF NOT EXISTS isxn_lookup (ISSN VARCHAR, normalized_isxn VARCHAR, normalized_title VARCHAR)")

    # load file
    con.execute("CREATE TABLE report AS SELECT * FROM read_xlsx(?)", [xlsx_file])

    # load lookup_tables
    con.execute("CREATE TABLE book_list AS SELECT * FROM './data_lookup_tables/book_list_wikidata.csv'")
    con.sql("UPDATE book_list SET isbn_13 = REPLACE(isbn_13, '-', '')")
    con.sql("UPDATE book_list SET isbn_10 = REPLACE(isbn_10, '-', '')")
    # con.sql("SELECT * FROM book_list").show()

    con.execute("CREATE TABLE journal_list AS SELECT * FROM './data_lookup_tables/journal_list_wikidata.csv'")
    # con.sql("SELECT * FROM journal_list").show()

    # Create a list of distinct ISSN column items
    issn_tuple = con.sql("SELECT DISTINCT ISSN FROM report WHERE COLUMNS('Request Type') = 'Article'").fetchall()
    issn_column = [item[0] for item in issn_tuple]
    logger.debug(issn_column)

    # TODO Add cleanup to catch extra characters ie. dashes in isbn

    # Create issn_list from issn_column
    issn_list = remove_non_issn(issn_column)
    logger.debug(issn_list)
    
    # Create isbn_list from issn_column
    isbn_list = remove_non_isbn(issn_column)
    logger.debug(isbn_list)
    
    # TODO Compare issn_list and isbn_list against isxn_lookup table. Remove matches from list.

    # Lookup requests for title by issn
    # issn_and_titles = issn_lookup(issn_list)
    # logger.debug(issn_and_titles)
    # if issn_and_titles:
        # con.executemany("INSERT INTO isxn_lookup VALUES (?, ?, ?)", issn_and_titles)
    # else:
        # logger.info("Scraped journal list is empty.")

    # Lookup requests for title by isbn
    # isbn_and_titles = isbn_lookup(isbn_list)
    # logger.debug(isbn_and_titles)
    # if isbn_and_titles:
        # con.executemany("INSERT INTO isxn_lookup VALUES (?, ?, ?)", isbn_and_titles)
    # else:
        # logger.info("Scraped book list is empty.")

    # Add columns and match new data in isxn_lookup to report and save file
    path = Path(xlsx_file)
    save_xlsx_file = path.parent / (path.stem + "_NORMALIZED" + path.suffix)
    con.sql(f"COPY (SELECT * FROM report LEFT OUTER JOIN journal_list on report.ISSN = journal_list.issn LEFT OUTER JOIN book_list on report.ISSN = book_list.isbn_13) TO '{save_xlsx_file}' WITH (FORMAT xlsx, HEADER true)")

    # con.sql(f"COPY (SELECT * FROM report LEFT OUTER JOIN isxn_lookup on report.ISSN = isxn_lookup.ISSN) TO '{save_xlsx_file}' WITH (FORMAT xlsx, HEADER true)")

    
def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

    logger.info("Starting")
    normalize()


if __name__ == "__main__":
    main()