import logging
import requests
import time
import xml.etree.ElementTree as ET

from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

logger = logging.getLogger(__name__)


# Iterate through the transaction list and search for corresponding ISSNs and titles from CrossRef
def issn_lookup(issn_list):
    issn_and_titles = []
    for x_issn in issn_list:

        api_url = f"https://api.crossref.org/journals/{x_issn}"
        try:
            headers = {'User-Agent': 'ISSN-info/1.0 (mailto:myexample@email.com)'}
            response = requests.get(api_url, headers=headers)
            data = response.json()
            # Retrieve the ISSN and title from the response
            if "message" in data:
                journal_info = data["message"]
                if "ISSN" in journal_info:
                    issn = journal_info["ISSN"][0]
                if "title" in journal_info:
                    journalLabel = journal_info["title"]
                    issn_and_titles.append(tuple((journalLabel, issn)))

        except HTTPError:
            logger.exception("Crossref exception HTTP error occurred")
        except ConnectionError:
            logger.exception("Crossref exception Connection error occurred")
        except Timeout:
            logger.exception("Crossref exception Timeout error occurred")
        except RequestException:
            logger.exception("Crossref exception An error occurred")
        else:
            logger.info("Crossref Request was successful.")

    return issn_and_titles      

def isbn_lookup_lc(isbn_list):
    isbn_and_titles = []
    for x_isbn in isbn_list:
        time.sleep(5)
        try:
            url = 'http://lx2.loc.gov:210/lcdb?version=1.1&operation=searchRetrieve&query=' + str(x_isbn) + '&startRecord=1&maximumRecords=5&recordSchema=mods'
            response = requests.get(url)
            tree = ET.fromstring(response.text)

            # Find the title element and extract the title text
            title_element = tree.find('.//{http://www.loc.gov/mods/v3}title')
            if title_element is not None:
                new_title = title_element.text
                if len(x_isbn) > 12:
                    isbn10 = None
                    isbn13 = x_isbn
                else:
                    isbn10 = x_isbn
                    isbn13 = None
                    
                isbn_and_titles.append(tuple((new_title, isbn10, isbn13)))
                    
        except HTTPError:
            logger.exception("LoC exception HTTP error occurred")
        except ConnectionError:
            logger.exception("LoC exception Connection error occurred")
        except Timeout:
            logger.exception("LoC exception Timeout error occurred")
        except RequestException:
            logger.exception("LoC exception An error occurred")
        else:
            logger.info("LoC Request was successful.")

    return isbn_and_titles
