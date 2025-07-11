import logging
import requests
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
        
# Iterate through the transaction list and search for corresponding ISSNs and titles from Google Books
def isbn_lookup_google(isbn_list):
    isbn_and_titles = []
    for x_isbn in isbn_list:
    
        try:
            api_key = "AIzaSyAvvo85uFwMwPVtpsPczXcQjX2Y1Iok0EI"
            url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + x_isbn + "&key=" + api_key
            response = requests.get(url)
            book_data = response.json()
            
            if 'items' in book_data:
                items = book_data['items']
                if len(items) > 0:
                    volume_info = items[0]['volumeInfo']
                    new_isbn = volume_info['industryIdentifiers'][0]['identifier']
                    new_title = volume_info['title']
                    logger.debug(f"{new_isbn} , {new_title}")
                    isbn_and_titles.append(tuple((x_isbn, new_isbn, new_title)))
            if 'error' in book_data:
                logger.debug(f"Error")
                    
        except HTTPError:
            logger.exception("Google Books exception HTTP error occurred")
        except ConnectionError:
            logger.exception("Google Books exception Connection error occurred")
        except Timeout:
            logger.exception("Google Books exception Timeout error occurred")
        except RequestException:
            logger.exception("Google Books exception An error occurred")
        else:
            logger.info("Google Books Request was successful.")

    return isbn_and_titles


def isbn_lookup_lc(isbn_list):
    isbn_and_titles = []
    for x_isbn in isbn_list:
    
        try:
            url = 'http://lx2.loc.gov:210/lcdb?version=1.1&operation=searchRetrieve&query=' + x_isbn + '"&startRecord=1&maximumRecords=5&recordSchema=mods'
            response = requests.get(url)
            xml_data = response.json()
            root = ET.fromstring(xml_data)
            
            # Find the title element and extract the title text
            title_element = root.find('title')
            if title_element is not None:
                new_title = title_element.text
                logger.debug(f"{x_isbn} , {new_title}")
                isbn_and_titles.append(tuple((x_isbn, new_title)))
            if 'error' in xml_data:
                logger.debug(f"Error")
                    
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
