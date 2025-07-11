
import logging
import requests
import xml.etree.ElementTree as ET

from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout, JSONDecodeError

logger = logging.getLogger(__name__)

def isbn_lookup_lc(isbn_list):
    isbn_and_titles = []
    for x_isbn in isbn_list:
    
        try:
            url = 'http://lx2.loc.gov:210/lcdb?version=1.1&operation=searchRetrieve&query=' + str(x_isbn) + '&startRecord=1&maximumRecords=5&recordSchema=mods'
            response = requests.get(url)
            tree = ET.fromstring(response.text)

            print(response.text)
            print(f'_____')
            print(tree.text)
            print(f'_____')
            print(tree.findall('{http://www.loc.gov/mods/v3}recordInfo'))
            # root = tree.getroot()

            # for title in root.findall('title'):
                # print(title.tag, title.attrib)

            # Find the title element and extract the title text
            # for records in root.findall('records'):
                # print(records)
                # title_element = records.find('record.recordData.mods.titleInfo')
                # print(title_element.text)
                # if title_element is not None:
                    # new_title = title_element.text
                    # logger.debug(f"{x_isbn} , {new_title}")
                    # isbn_and_titles.append(tuple((x_isbn, new_title)))
                # if 'error' in records:
                    # logger.debug(f"Error")
                    
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

    return isbn_and_titles


def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

    isbn_list = [9780060777579]
    isbn_lookup_lc(isbn_list)
    


if __name__ == "__main__":
    main()