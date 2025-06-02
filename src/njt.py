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
    con = duckdb.connect(':memory:')

    # load file
    con.execute("CREATE TABLE report AS SELECT * FROM read_xlsx(?)", [xlsx_file])

    # Create a list of distinct ISSN column items
    issn_tuple = con.sql("SELECT DISTINCT ISSN FROM report WHERE COLUMNS('Request Type') = 'Article'").fetchall()
    issn_column = [item[0] for item in issn_tuple]
    logger.debug(issn_column)

    # Create issn_list from issn_column
    issn_list = remove_non_issn(issn_column)
    logger.debug(issn_list)
    
    # Create isbn_list from issn_column
    isbn_list = remove_non_isbn(issn_column)
    logger.debug(isbn_list)
    
    # Lookup requests for title by isxn
    issn_and_titles = issn_lookup(issn_list)
    logger.debug(issn_and_titles)

    # Lookup requests for title by isbn
    isbn_and_titles = isbn_lookup(isbn_list)
    logger.debug(isbn_and_titles)
    
    # Add columns with new data

    # save file
    path = Path(xlsx_file)
    save_xlsx_file = path.parent / (path.stem + "_NORMALIZED" + path.suffix)
    con.sql(f"COPY report TO '{save_xlsx_file}' WITH (FORMAT xlsx)")

    

def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

    logger.info("Starting")
    normalize()


if __name__ == "__main__":
    main()