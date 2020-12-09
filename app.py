# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -
import subprocess, platform, json, time, uuid, csv, ctypes, sys, random
import datetime
from datetime import datetime
# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -

try:
    import requests
    from colorama import init, Fore, Back, Style
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'colorama'])

# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# Initializing Colorama || Utils
init(convert=True) if platform.system() == "Windows" else init()
print(f"{Fore.CYAN} {Style.BRIGHT} --- Script Created by @ayyitsc9 ---\n")
ctypes.windll.kernel32.SetConsoleTitleW("Nike Order Checker ~ By @ayyitsc9")
# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# Initializing Settings
def init():
    # For variables from settings.json file
    global delay, use_proxies, input_file_name, output_file_name, bnb_import_file
    with open("settings.json", "r") as settings:
        data = json.load(settings)
        delay = data['delay']
        use_proxies = data['use_proxies']
        input_file_name = data['input_file_name']
        output_file_name = data['output_file_name']
        bnb_import_file = data['import']['bnb_file_name']
    
    # For data from .csv file
    global orders
    orders = []
    with open(input_file_name, newline='') as input_file:
        csv_file = csv.reader(input_file)
        try:
            for row in csv_file:
                if row != ["Order Email", "Order Number"]:
                    orders.append((row[0], row[1]))
        except Exception as e:
            Logger.error(f"Error : {e}")

    # For proxies
    if use_proxies:
        global proxy_file, proxy_list
        proxy_file = open("proxies.txt", "r")
        proxy_list = proxy_file.read().split("\n")
        proxy_file.close()

    # Other Variables
    global success, failed
    success = 0
    failed = 0

# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -

lightblue = "\033[94m"
orange = "\033[33m"

class Logger:
    @staticmethod
    def timestamp():
        return str(datetime.now())[:-7]
    @staticmethod
    def normal(message):
        print(f"{lightblue}[{Logger.timestamp()}] {message}")
    @staticmethod
    def other(message):
        print(f"{orange}[{Logger.timestamp()}] {message}")
    @staticmethod
    def error(message):
        print(f"{Fore.RED}[{Logger.timestamp()}] {message}")
    @staticmethod
    def success(message):
        print(f"{Fore.GREEN}[{Logger.timestamp()}] {message}")

# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -

class Proxy:
    @staticmethod
    def format_proxy(full_proxy, proxy_type):
        proxy_type = proxy_type
        full_proxy = full_proxy
        if proxy_type == "UP":
            proxy_username = full_proxy.split(":")[2]
            proxy_password = full_proxy.split(":")[3]
            proxy_ip = full_proxy.split(":")[0]
            proxy_port = full_proxy.split(":")[1]
            return  {
                "http": f"http://{proxy_username}:{proxy_password}@{proxy_ip}:{proxy_port}", 
                "https": f"http://{proxy_username}:{proxy_password}@{proxy_ip}:{proxy_port}"
                }
        elif proxy_type == "IP":
            return  {
                "http": f"http://{full_proxy}", 
                "https": f"http://{full_proxy}"
                }
        else:
            return {
                "http": None, 
                "https": None
                }

    @staticmethod
    def get_proxy(proxy_list):
        proxy_list = proxy_list
        full_proxy = random.choice(proxy_list)
        if len(full_proxy.split(":")) == 2:
            proxy_type = "IP"
        elif len(full_proxy.split(":")) == 4:
            proxy_type = "UP"
        else:
            Logger.error("Invalid proxy format detected! Using localhost...")
            proxy_type = "LH"
        formatted_proxy = Proxy.format_proxy(full_proxy, proxy_type)
        return formatted_proxy

# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -

class NikeOrderCheck:
    def __init__(self, order_email, order_number):
        global success, failed
        self.order_email, self.order_number, self.success, self.failed = order_email, order_number, success, failed
        # Generate uuid v4 for visitorid value
        self.uuid = self.generate_uuid_v4()
        # Get status of the order
        Logger.normal(f"[{self.order_email}][{self.order_number}] Getting order status...")
        self.order = self.get_order_status()
        # Updating the global variable success and failed
        success, failed = self.success, self.failed
        # Checks if we got a valid response when trying to get order status
        if self.order:
            self.save_to_csv()

    def generate_uuid_v4(self):
        return str(uuid.uuid4())

    def get_order_status(self):
        # For reference, user-agent is not a required header but I still included it!
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-nike-visitorid":self.uuid,
            "x-nike-visitid":"1",
            "appid":"orders"
        }
        # Checks if use_proxies is True
        if use_proxies:
            response = requests.get(f"https://api.nike.com/order_mgmt/user_order_details/v2/{self.order_number}?filter=email({self.order_email})", headers=headers, proxies=Proxy.get_proxy(proxy_list))
        else:
            response = requests.get(f"https://api.nike.com/order_mgmt/user_order_details/v2/{self.order_number}?filter=email({self.order_email})", headers=headers)
        # Checking if the request was successful
        if response.status_code == 200:
            Logger.success(f"[{self.order_email}][{self.order_number}] Got order status!")
            self.success += 1
            return response.json()
        else:
            Logger.error(f"[{self.order_email}][{self.order_number}] Failed to get order status! Error : {response.status_code}")
            self.failed += 1
            return False

    def save_to_csv(self):
        with open(output_file_name, 'a+', newline='') as output_file:
            csv_file = csv.writer(output_file)
            # Passing in a list of values that we want the row to contain. In this case : [order_date, product_sku, product_size, order_status, order_email, order_number, address, credit_card_last_4, order_total]
            data = [
                self.order['orderCreateDate'], 
                f"{self.order['orderLines'][0]['styleNumber']}-{self.order['orderLines'][0]['colorCode']}", 
                self.order['orderLines'][0]['displaySize'], 
                self.order['status'], 
                self.order_email, 
                self.order_number,
                f"{self.order['orderLines'][0]['shipTo']['address']['address1']} {self.order['orderLines'][0]['shipTo']['address']['city']}, {self.order['orderLines'][0]['shipTo']['address']['state'] if 'state' in self.order['orderLines'][0]['shipTo']['address'].keys() else ''} {self.order['orderLines'][0]['shipTo']['address']['zipCode']}, {self.order['orderLines'][0]['shipTo']['address']['country']}",
                self.order['paymentMethods'][0]['displayCreditCardNumber'],
                self.order['totalAmount']
            ]
            # Appends to the csv file (Adds one line)
            csv_file.writerow(data)
            output_file.close()

# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -

class Importer:
    @staticmethod
    def bnb():
        # This list will contain lists containing order email and order number Example : [["test@gmail.com", "C01234"], ["test2@gmail.com", "C012345"]]
        import_data = []
        # Opening bnb import file
        with open(bnb_import_file, newline='') as import_file:
            import_csv_file = csv.reader(import_file)
            try:
                for row in import_csv_file:
                    import_data.append([row[0], row[1]])
            except Exception as e:
                Logger.error(f"Error : {e}")
            import_file.close()
        
        # Opening input file
        with open(input_file_name, 'a+', newline='') as input_file:
            input_csv_file = csv.writer(input_file)
            # Appends to the csv file (Adds one line per order list in import_data)
            input_csv_file.writerows(import_data)
            input_file.close()
        Logger.success(f"Successfully imported BNB data from {bnb_import_file}!")


# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -

while True:
    print(Style.RESET_ALL)
    print("What would you like to do?\n")
    print("######################################\n")
    print("[1]Run Order Checker\t\t[2]BNB Import\n")
    print("[3]Exit\n")
    print("######################################\n")
    task = input("Enter Option : ")
    print("\n")
    if task == "1":
        init()
        for order in orders:
            NikeOrderCheck(order[0], order[1])
            Logger.success("Finished Order Checker Execution!")
            ctypes.windll.kernel32.SetConsoleTitleW(f"Nike Order Checker ~ By @ayyitsc9 | Success : {str(success)} | Failed : {str(failed)}")
            time.sleep(delay)
    elif task == "2":
        init()
        Importer.bnb()
    elif task == "3":
        Logger.other("Comment on my legit check @ https://twitter.com/ayyitsc9")
        Logger.other("Star the repository @ https://github.com/ayyitsc9/nike-order-checker")
        Logger.error("Exiting in 5 seconds...")
        time.sleep(5)
        sys.exit()
    else:
        print("Invalid input. Try again!")

