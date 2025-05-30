import logging
import requests

from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

logger = logging.getLogger(__name__)


# Iterate through the transaction list and search for corresponding ISSNs and titles from CrossRef
def issn_lookup(issn_list):
    issn_and_titles = []
    for x_issn in issn_list:
        # x = str(x)
        # new_df.loc[idx, 'original'] = x
        # x_short = x.replace("-", "").replace(" ", "").strip()
        # if len(x_short) == 8:
        #     x_issn = x_short[0:4] + "-" + x_short[4:8]

        api_url = f"https://api.crossref.org/journals/{x_issn}"
        try:
            headers = {'User-Agent': 'ISSN-info/1.0 (mailto:myexample@email.com)'}
            response = requests.get(api_url, headers=headers)
            data = response.json()
            # Retrieve the ISSN and title from the response
            if "message" in data:
                journal_info = data["message"]
                if "ISSN" in journal_info:
                    new_issn = journal_info["ISSN"][0]
                if "title" in journal_info:
                    new_title = journal_info["title"]
                issn_and_titles.append(tuple((new_issn, new_title)))
                logger.debug(new_issn, new_title)

        except HTTPError:
            logger.exception("Crossref exception HTTP error occurred: {http_err}")
        except ConnectionError:
            logger.exception("Crossref exception Connection error occurred: {conn_err}")
        except Timeout:
            logger.exception("Crossref exception Timeout error occurred: {timeout_err}")
        except RequestException:
            logger.exception("Crossref exception An error occurred: {req_err}")
        else:
            logger.info("Crossref Request was successful.")

    # logger.debug(issn_and_titles)
    return issn_and_titles
        
# Iterate through the transaction list and search for corresponding ISSNs and titles from Google Books
# def isbn_lookup(isbn_list):
    # elif len(x_short) == 13 or len(x_short) == 10:
        # try:
            # api_key = "AIzaSyAvvo85uFwMwPVtpsPczXcQjX2Y1Iok0EI"
            # url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + x_short + "&key=" + api_key
            # response = requests.get(url)
            # book_data = response.json()
            # 
            # if 'items' in book_data:
                # items = book_data['items']
                # if len(items) > 0:
                    # volume_info = items[0]['volumeInfo']
                    # new_df.loc[idx, 'issn'] = volume_info['industryIdentifiers'][0]['identifier']
                    # new_df.loc[idx, 'title'] = volume_info['title']
                    # 
        # except HTTPError:
            # logger.exception("Google Books exception HTTP error occurred: {http_err}")
        # except ConnectionError:
            # logger.exception("Google Books exception Connection error occurred: {conn_err}")
        # except Timeout:
            # logger.exception("Google Books exception Timeout error occurred: {timeout_err}")
        # except RequestException:
            # logger.exception("Google Books exception An error occurred: {req_err}")
        # else:
            # logger.info("Google Books Request was successful.")