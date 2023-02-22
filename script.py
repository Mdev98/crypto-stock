import requests
from bs4 import BeautifulSoup
import logging
import json
from pathlib import Path

path_to_log = Path(__file__).resolve().parent / 'app.log'
path_to_data = Path(__file__).resolve().parent / 'data.json'



# Set up logging with a log file named "app.log"
# The log will contain the log level, the log message, and the timestamp of the log message

logging.basicConfig(level=logging.INFO,
                    filename=path_to_log,
                    filemode="a",
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug(path_to_log)
logging.debug(path_to_data)

# Define the URL to scrape
url = "https://coinmarketcap.com/"

# Make an HTTP GET request to the URL
r = requests.get(url)


def get_links()-> set[str]:
    """ This function returns a list of URLs for all the cryptocurrency pages on the site.

    Returns:
        Set[str]: set of links of all cryptocurrencies
    """

    # Check if the request is successful
    if r.status_code == 200:
        # Get the content on the response
        content = r.content
        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(content, 'html.parser')
        # Find all the "a" tags with the class "cmc-link"
        all_anchor = soup.find_all(name='a', class_='cmc-link')
        links = []
        #Iterate through "a" tags
        for tag in all_anchor:
            tag = str(tag.get('href'))
            # Filter out the URLs that start with "/currencies"
            if tag.startswith("/currencies"):
                liste = tag.split(sep='/')
                tag = '/'.join(liste[1:3])
                links.append(tag)
        # Remove duplicates from the list of links
        links = set(links)
        # Return the list of link
        return links
    else:
        # Return an empty list if the request is unsuccessful
        return set()

def scrape_crypto_data():
    """
        This function scrapes data for all cryptocurrencies on the site and saves the data to a JSON file.
    """
    # Get list of links
    links = get_links()
    all_data = []
    # Iterate over the list
    for i, link in enumerate(links):

        try:
            # Make a request to the URL
            r = requests.get(f"{url}{link}")
            # Check if the request is successful
            if r.status_code == 200:
                # Parse the HTML content with BS$
                soup = BeautifulSoup(r.content, 'html.parser')
                # Find the name of the cryptocurrency
                crypto_name = soup.find(name='span', class_='sc-1d5226ca-1').string
                # Find the symbol of the cryptocurrency
                crypto_symbol = soup.find(name='small', class_='nameSymbol').string
                # Find the price of the cryptocurrency
                crypto_price = soup.find(name='div', class_='priceValue').next_element.string.split('$')[1]
                # Find the rate of the cryptocurrency
                stats = soup.find(class_="sc-aef7b723-0 RdAHw").find_next(name='td').find_next(name='td').find_next(name='span').next_element.get_text().split("$")
                crypto_rate = {
                    'up-down' : stats[0],
                    'value' : stats[-1]
                }
                # Build the data
                data = {
                    'name' : crypto_name,
                    'symbol' : crypto_symbol,
                    'price' : crypto_price,
                    'rate' : crypto_rate
                }
                # Add the data to the list
                all_data.append(data)
        except Exception as e:
            # Log an error if occurs
            logging.info(f"An error occurred: {e}")

    store_in_file(all_data)

def store_in_file(data):

    """
        Store all the data in a file
    """
    with open(path_to_data, 'w') as file:
        json.dump(data, file, indent=4)
    logging.info("Data save successfully")

if __name__ == '__main__':
    scrape_crypto_data()
