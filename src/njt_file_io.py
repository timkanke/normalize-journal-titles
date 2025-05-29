import click
import duckdb
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

@click.command()
@click.argument('xlsx_file', type=click.Path(exists=True))
def normalize(xlsx_file):
    con = duckdb.connect(':memory:')

    # load file
    con.execute("CREATE TABLE report AS SELECT * FROM read_xlsx(?)", [xlsx_file])
    con.sql("SELECT * FROM report").show()

    # save file
    path = Path(xlsx_file)
    save_xlsx_file = path.parent / (path.stem + "_NORMALIZED" + path.suffix)
    con.sql(f"COPY report TO '{save_xlsx_file}' WITH (FORMAT xlsx)")

    

def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    logger.info("Starting Import")
    normalize()


if __name__ == "__main__":
    main()