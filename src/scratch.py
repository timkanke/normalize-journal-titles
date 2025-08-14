
import logging
import requests
import time
import xml.etree.ElementTree as ET

from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout, JSONDecodeError

logger = logging.getLogger(__name__)

def isbn_lookup_lc(isbn_list):
    isbn_and_titles = []
    for x_isbn in isbn_list:
        time.sleep(5)
        try:
            url = 'http://lx2.loc.gov:210/lcdb?version=1.1&operation=searchRetrieve&query=' + str(x_isbn) + '&startRecord=1&maximumRecords=5&recordSchema=mods'
            response = requests.get(url)
            tree = ET.fromstring(response.text)
            # ns = {'m': 'http://www.loc.gov/mods/v3'}

            print(response.text)
            print(f'_____')

            # Find the title element and extract the title text
            title_element = tree.find('.//{http://www.loc.gov/mods/v3}title')
            if title_element is not None:
                new_title = title_element.text
                print(f"Title: {title_element.text}")
                isbn_and_titles.append(tuple((x_isbn, new_title)))

        except HTTPError:
            logger.exception("LoC exception HTTP error occurred")
        except ConnectionError:
            logger.exception("LoC exception Connection error occurred")
        except Timeout:
            logger.exception("LoC exception Timeout error occurred")
        except JSONDecodeError:
            logger.exception("LoC exception JSON Decode error occurred")
        except RequestException:
            logger.exception("LoC exception An error occurred")
        else:
            logger.info("LoC Request was successful.")

    # print(isbn_and_titles)
    return isbn_and_titles


def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
    
    isbn_list = [9780060777579, 9780123693983, 9780078021770]
    isbn_lookup_lc(isbn_list)    
    isbn_and_titles = isbn_lookup_lc(isbn_list)
    logger.debug(isbn_and_titles)


if __name__ == "__main__":
    main()