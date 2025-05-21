import logging

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    logger.info("Hello from normalize-joural-titles!")


if __name__ == "__main__":
    main()
