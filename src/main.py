import click
import csv
import logging

logger = logging.getLogger(__name__)

@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
def import_csv(csv_file):
    """Imports data from a CSV file and prints it to the console."""
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            click.echo(row)

def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    logger.info("Hello from normalize-joural-titles!")
    import_csv()


if __name__ == "__main__":
    main()
