from scraping import scrape_transaction_data
from api_operations import process_address

if __name__ == "__main__":
    scraped_data = scrape_transaction_data(url="https://etherscan.io/txs")
    for idx, address in scraped_data.items():
        process_address(idx, address)

