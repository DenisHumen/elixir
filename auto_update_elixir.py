import requests
import mysql.connector
import time
import paramiko
from tqdm import tqdm


base = {
    'user': 'root',
    'passwd': 'YOUR PASSWROD',
    'host': 'IP FOR SERVER MYSQL',
    'database': 'DATA',
    'raise_on_warnings': True
}


#Функция получает последнее обновление из docker hub
def get_last_updated(repository):
    url = f"https://hub.docker.com/v2/repositories/{repository}/tags"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                last_updated = data["results"][0]["last_updated"]
                return last_updated
            else:
                return "No tags found"
        else:
            return f"Failed to fetch data. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"




ip_nodes = []
mysql_value_last_update_nodes =[]

def last_update_nodes():
    global ip_nodes
    global mysql_value_last_update_nodes

    def base_value(values):
        connect = mysql.connector.connect(**base)
        if connect.is_connected():
            None
        else:
            raise Exception('Ошибка подключения к базе')
        cursor = connect.cursor()
        query = f'SELECT {values} FROM elixir'
        cursor.execute(query)
        result = cursor.fetchall()
        updates = list(result)
        updates = ['-' if x is None else x for x in updates]
        updates = [row[0] for row in result]

        cursor.close()
        connect.close()

        return updates
    
    ip_nodes = base_value('gray_ip')
    mysql_value_last_update_nodes = base_value('last_updated')
    


def update_values_last_update(version_container, ip):
    print(f'Последняя версия контейнера была записана в базе {version_container}')
    connect = mysql.connector.connect(**base)
    if connect.is_connected():
        None
    else:
        raise Exception('Ошибка подключения к базе в функции update_values_last_update')
    cursor = connect.cursor()
    query = "UPDATE elixir SET last_updated = %s WHERE gray_ip = %s;"
    cursor.execute(query, (version_container, ip))
    connect.commit()

    print(version_container)
    print(ip)

    cursor.close()
    connect.close()



def update_nodes(ip):
    print(f'Обновление ноды {ip}')
    username = 'root'
    password = 'PASSWORD ELIXIR'
    port = 22

    try:
        command = 'bash <(curl -s https://raw.githubusercontent.com/MeSmallMan/scripts/main/elixir_update.sh)'
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f'Подключеник к {ip} для обновелния ноды')
        client.connect(ip, port, username, password)

        print(f'Выполнение команды для обновелния {command}')
        stdin, stdout, stderr = client.exec_command(command)

        result = stdout.read().decode()
        error = stderr.read().decode()

        if result:
            print('Результат выполнения команды: ')
            print(result)
        if error:
            print('Ошибка обновелния: ')
            print(error)
        
    except Exception as e:
        print(f'Ошибка подключения к {ip} Ошибка = {e}')
    finally:
        client.close()




def main():
    last_update_nodes()

    last_update = get_last_updated("elixirprotocol/validator") # Проверка последнего обновелния в в docker hub
    print(f"Last updated: {last_update}")

    # Проверка обновелния docker hub == mysql values
    index = -1
    for index, update in tqdm(enumerate(mysql_value_last_update_nodes), total=len(mysql_value_last_update_nodes), desc="Processing updates", colour='#009FBD'):

        if update == last_update:
            time.sleep(3)
        else:
            update_nodes(ip_nodes[index])
            time.sleep(3)
            update_values_last_update(last_update, ip_nodes[index])
        
        
main()
