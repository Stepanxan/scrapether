import time
import requests
from bs4 import BeautifulSoup
import json

# Скрапінг сайту для отримання останніх 5-ти транзакцій та витягування з них гаманця(From) який записується в scraped_data.json
def scrape_transaction_data(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        text_break_elements = soup.find_all("a", class_="text-break")
        if len(text_break_elements) > 0:
            data_to_store = text_break_elements[0].get_text().strip()
            return data_to_store
    return {}


url = "https://etherscan.io/txs"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    start_scraping_time = time.time()
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("span", class_="hash-tag text-truncate")
    transaction_items = list(filter(lambda item: item.get_text().strip().startswith("0"), items))
    # Ліміт можна змінювати. На сторінці одночасно показано 50 транзакцій.
    transaction_items = transaction_items[:10]

    data_list = []
    for item in transaction_items:
        info_text = item.get_text().strip()
        data_list.append(info_text)
    print("Selected Data:")
    for idx, item in enumerate(data_list):
        print(f"{idx + 1}: {item}")

    scraped_data = {}
    for idx, item in enumerate(data_list):
        transaction_url = f"https://etherscan.io/tx/{item}"
        data = scrape_transaction_data(transaction_url)
        if data:
            scraped_data[idx + 1] = data

    end_scraping_time = time.time()
    print(f"Scraping took {end_scraping_time - start_scraping_time} seconds")
    with open("scraped_data.json", "w", encoding="utf-8") as json_file:
        json.dump(scraped_data, json_file, ensure_ascii=False, indent=4)
    print("Scraped data saved to 'scraped_data.json'")
else:
    print("Request Error:", response.status_code)



