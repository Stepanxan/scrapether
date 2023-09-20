import time
import json
import requests
from datetime import datetime
import threading
from queue import Queue


# За допомогою Арі сайту витягуємо з scraped_data.json по черзі всі кошильки, підставляємо їх в url(address) і так ми переходимо на сторінку гаманця з якої
# використовуючи функції get_transactions дістаємо всю потрібну інформацію про передостанню транзакцію яка відбулась більше або включно 100 днів тому і якщо вона
# 2 в списку транзакцій записуємо результат в result.json
API_KEY = "USF8W6J5JV25TUYBZ45IY276ZR2SFQRAEH"
BASE_URL = "https://api.etherscan.io/api"
ETHER_VALUE = 10 ** 18

def make_api_url(module, action, address, **kwargs):
    url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={API_KEY}"
    for key, value in kwargs.items():
        url += f"&{key}={value}"
    return url

def get_previous_transaction(address):
    get_transactions_url = make_api_url("account", "txlist", address, startblock=0, endblock=99999999, page=1, offset=2, sort="desc")
    response = requests.get(get_transactions_url)
    data = response.json()["result"]

    if len(data) >= 2:
        start_get_transaction_time = time.time()
        tx = data[1]
        previous_tx = data[0]
        current_date = datetime.now()
        transaction_date = datetime.fromtimestamp(int(tx['timeStamp']))
        difference = current_date - transaction_date

        if difference.days > 1 and tx != previous_tx:
            transaction_hash = tx["hash"]
            to = tx["to"]
            from_addr = tx["from"]
            value = tx["value"]
            gas = int(tx["gasUsed"]) * int(tx["gasPrice"]) / ETHER_VALUE

            transaction_time = datetime.fromtimestamp(int(tx['timeStamp']))
            transaction_result = {
                "Transaction Hash": transaction_hash,
                "To": to,
                "From": from_addr,
                "Value": value,
                "Gas Used": gas,
                "Time": transaction_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            end_get_transaction_time = time.time()
            print(f"get_previous_transaction took {end_get_transaction_time - start_get_transaction_time} seconds")
            return transaction_result

        return None

with open("scraped_data.json", "r", encoding="utf-8") as json_file:
    scraped_data = json.load(json_file)

result_data = {}
result_data_lock = threading.Lock()
result_queue = Queue()

while not result_queue.empty():
    idx, data = result_queue.get()
    result_data[idx] = data
def process_address(idx, address):
    print(f"Processing Address {idx}: {address}")
    previous_transaction = get_previous_transaction(address)

    if previous_transaction:
        with result_data_lock:
            result_data[idx] = {
                "Address": address,
                "Previous Transaction": previous_transaction
            }
    time.sleep(5)
threads = []
for idx, address in scraped_data.items():
    thread = threading.Thread(target=process_address, args=(idx, address))
    threads.append(thread)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

with open("result.json", "w", encoding="utf-8") as result_file:
    json.dump(result_data, result_file, ensure_ascii=False, indent=4)
print("Processed data saved to 'result.json'")