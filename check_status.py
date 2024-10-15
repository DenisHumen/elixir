import requests
import mysql.connector
import time
import random
from tqdm import tqdm



base = { 
    'user': 'USER',
    'passwd': 'PASSWD',
    'host': 'IP ADDRESS',
    'database': 'DATABASE',
    'raise_on_warnings': True
}

connect = mysql.connector.connect(**base)
cursor = connect.cursor()

def select_data():
    if connect.is_connected():
        pass
    else:
        raise Exception('Ошибка при подключении к базе')
    
    query = 'SELECT wallet_address FROM elixir'
    cursor.execute(query)
    wallet = cursor.fetchall()
    
    addresses = [address[0] for address in wallet]
    return addresses



def write_result(wallet, online, uptime_week):
    online_value = '🟢' if online else '❌' if online is not None else 'ОШИБКА-ПРОВЕРИТЬ'
    
    query = f"""
    UPDATE elixir 
    SET online = '{online_value}', 
        uptime_week = '{uptime_week}' 
    WHERE wallet_address = '{wallet}'
    """
    
    cursor.execute(query) 
    connect.commit()


def proxy_mysql():
    random_proxy = random.randint(1, 705)
    connect = mysql.connector.connect(**base)
    if not connect.is_connected():
        raise Exception('Ошибка при подключении к базе')

    cursor = connect.cursor()
    query = f'SELECT IP FROM proxy WHERE id = "{random_proxy}"'
    cursor.execute(query)
    result = cursor.fetchall()
    if len(result) == 0:
        raise IndexError(f'Прокси с id {random_proxy} не найдено')
    
    return result[0][0]


def responce(wallet_address, proxy):
    url = f"https://api.testnet-3.elixir.xyz/validators//{wallet_address}"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    proxies = {
        "http": f"http://skorikannasergeevna:mMFVerY4o2@{proxy}:59100",
        "https": f"http://skorikannasergeevna:mMFVerY4o2@{proxy}:59100"
    }

    max_retries = 3
    attempts = 0
    while attempts < max_retries:
        try:
            response = requests.get(url, headers=headers, proxies=proxies)
            if response.status_code == 200:
                data = response.json()
                return(data)
            else:
                print(f"Ошибка: {response.status_code} - {response.text}")
        except requests.exceptions.ProxyError as e:
            pass
        except requests.exceptions.RequestException as e:
            pass
#        except 
        attempts +=1



def main():
    wallet_list = select_data() 
    green_bar_format = "\033[92m{l_bar}{bar}{r_bar}\033[0m"  

    for wallet in tqdm(wallet_list, desc='Processing wallets', unit='wallet', bar_format=green_bar_format):
        max_retries = 3  
        attempts = 0  

        while attempts < max_retries:
            proxy_address = proxy_mysql()
            responce_value = responce(wallet, proxy_address)
            
            if responce_value is not None:  
                break  
            else:  
                attempts += 1 
                time.sleep(5) 
        
        if responce_value is None:  
            continue  
        
        try:
            validator_data = responce_value.get('validator', {})
            online = validator_data.get('online')
            uptime_week = validator_data.get('uptime_week')

            if online is None or uptime_week is None:
                continue
                
            uptime_week = f'{uptime_week * 100:.1f}'
            write_result(wallet, online, uptime_week) 

        except Exception as e:
            print(f'error = {e}')

    
    connect.close() 
    cursor.close()  

main()

