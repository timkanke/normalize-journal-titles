import click
import logging
import pandas as pd
import os
import requests

from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

logger = logging.getLogger(__name__)

@click.command()
@click.argument('xlsx_file', type=click.Path(exists=True))
def normalize_data(xlsx_file):
    excel_object = pd.ExcelFile(xlsx_file)
    df_all = pd.read_excel(xlsx_file, sheet_name = excel_object.sheet_names[0], engine='openpyxl')
    df_all.info()

    # Select Data
    ill_df = pd.read_excel(xlsx_file, usecols=["Transaction Number",\
    "Request Type", "Process Type", "Photo Journal Title",\
    "Photo Journal Year", "ISSN", "Creation Date", "Status",\
    "Transaction Status", "Reason For Cancellation", "Document Type",\
    "Department"])
    
    # Filter for only Article requests
    filter = ill_df["Request Type"].isin(["Article"])
    article = ill_df[filter]
    article.info()

    # ISSN LOOK UP
    issn_list = list(article["ISSN"])
    transaction_list = list(article['Transaction Number'])

    # Initialize a new dataframe
    new_df = pd.DataFrame(columns=['Transaction Number', 'issn', 'title', 'original'])

    # Update the Transaction Number
    for idx, v in enumerate(transaction_list):
        new_df.loc[idx, 'Transaction Number'] = v

    # Iterate through the transaction list and search for corresponding ISSNs and titles from CrossRef
    for idx, x in enumerate(issn_list):
        x = str(x)
        new_df.loc[idx, 'original'] = x
        x_short = x.replace("-", "").replace(" ", "").strip()

        if len(x_short) == 8:
            x_issn = x_short[0:4] + "-" + x_short[4:8]
            
            api_url = f"https://api.crossref.org/journals/{x_issn}"
            
            try:
                headers = {'User-Agent': 'ISSN-info/1.0 (mailto:myexample@email.com)'}
                response = requests.get(api_url, headers=headers)
                data = response.json()
                
                # Retrieve the ISSN and title from the response
                if "message" in data:
                    journal_info = data["message"]
                    if "ISSN" in journal_info:
                        new_df.loc[idx, "issn"] = journal_info["ISSN"][0]
                    if "title" in journal_info:
                        new_df.loc[idx, "title"] = journal_info["title"]
                        
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
            
    # Iterate through the transaction list and search for corresponding ISSNs and titles from Google Books

        elif len(x_short) == 13 or len(x_short) == 10:
            try:
                api_key = "AIzaSyAvvo85uFwMwPVtpsPczXcQjX2Y1Iok0EI"
                url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + x_short + "&key=" + api_key
                response = requests.get(url)
                book_data = response.json()
                
                if 'items' in book_data:
                    items = book_data['items']
                    if len(items) > 0:
                        volume_info = items[0]['volumeInfo']
                        new_df.loc[idx, 'issn'] = volume_info['industryIdentifiers'][0]['identifier']
                        new_df.loc[idx, 'title'] = volume_info['title']
                        
            except HTTPError:
                logger.exception("Google Books exception HTTP error occurred: {http_err}")
            except ConnectionError:
                logger.exception("Google Books exception Connection error occurred: {conn_err}")
            except Timeout:
                logger.exception("Google Books exception Timeout error occurred: {timeout_err}")
            except RequestException:
                logger.exception("Google Books exception An error occurred: {req_err}")
            else:
                logger.info("Google Books Request was successful.")

    # Convert Transaction Number to numeric data type 

    issn_title_lookup = pd.DataFrame(new_df, columns=['Transaction Number', 'issn', 'title'])
    issn_title_lookup['Transaction Number'] = pd.to_numeric(issn_title_lookup['Transaction Number'], downcast='integer')
    issn_title_lookup.columns = ['Transaction Number', 'issn', 'title']

    """ UPDATE DATA """

    # Merge data and replace values
    def merge_data(df, lookup_df):
        # Merge data
        df_merged = pd.merge(df, lookup_df[['Transaction Number', 'issn', 'title']], how='left', on='Transaction Number')

        # Replace the "ISSN" in df with the corresponding values from lookup_df where available
        df_merged.loc[lookup_df['issn'].notnull(), 'ISSN'] = lookup_df.loc[lookup_df['issn'].notnull(), 'issn']

        # Replace the "Photo Journal Title" column in df with the corresponding values from lookup_df where available
        df_merged.loc[lookup_df['title'].notnull(), 'Photo Journal Title'] = lookup_df.loc[lookup_df['title'].notnull(), 'title']

        # Convert "Creation Date" to datetime and extract "year"
        df_merged['Creation Date'] = pd.to_datetime(df_merged['Creation Date']).dt.strftime('%Y-%m-%d')
        df_merged['year'] = pd.DatetimeIndex(df_merged['Creation Date']).year

        # Drop the 'issn' and 'TITLE' columns
        df_merged.drop(['issn', 'title'], axis=1, inplace=True)
        
        return df_merged

    # Update data with issn_title_lookup data
    df_updated = merge_data(article, issn_title_lookup)

    # Filter for Borrowing and Lending requests
    borrowing = df_updated[df_updated["Process Type"].isin(["Borrowing"])]
    lending = df_updated[df_updated["Process Type"].isin(["Lending"])]

    # Define the file names and dataframes
    file_names = []
    borrowing.name = 'borrowing'
    lending.name = 'lending'
    data_frames = [borrowing, lending]

    # Loop through the data frames and assign file name
    for data_frame in data_frames:
        file_name = os.path.basename(xlsx_file)
        file_name_without_extension, extension = os.path.splitext(file_name)
        save_name = f"{file_name_without_extension}_{data_frame.name}_NORMALIZED{extension}"
        file_names.append(save_name)

    # Save to files
    for file_name, data_frame in zip(file_names, data_frames):
        file_path = f"./example_data/{file_name}"
        data_frame.to_excel(file_path, index=False)
        logger.info(f"Saved {file_name}")


def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    logger.info("Hello from normalize-journal-titles!")
    normalize_data()


if __name__ == "__main__":
    main()
