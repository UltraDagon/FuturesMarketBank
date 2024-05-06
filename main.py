import mysql.connector
import json
import datetime

client_info = {"account_type": None, "username": None, "business_name": None}

def create_server_connection(host_name, user_name, user_password, database):
  connection = None
  try:
    connection = mysql.connector.connect(
      host=host_name,
      user=user_name,
      password=user_password,
      database=database
    )
    print("MySQL Database connection successful")
  except Exception as err:
    print(f"Error: '{err}'")

  return connection


mydb = create_server_connection("localhost", "root", "auto", "mydatabase")

cursor = mydb.cursor(buffered=True)
print(mydb.get_server_version())

def notification_count():
  if client_info["account_type"] == "user":
    cursor.execute(f"SELECT notifications FROM user_account WHERE (username = '{client_info['username']}')")

  if cursor.fetchall()[0] is None:
    return 0
  return len(cursor.fetchall())

def get_list(column):
  cursor.execute(f"SELECT {column} FROM user_account WHERE (username = '{client_info['username']}')")

  get = cursor.fetchall()[0][0]

  if get is None:
    return []
  return list(json.loads(get))

def get_balance(type, name):
  if type == "user":
    cursor.execute(f"SELECT balance FROM user_account WHERE (username = '{name}')")
  if type == "business":
    cursor.execute(f"SELECT balance FROM business WHERE (business_name = '{name}')")
  return cursor.fetchall()[0][0]

def change_settings():
  while True:
    print("--- Settings ---")
    cursor.execute(f"SELECT listed FROM user_account WHERE username = '{client_info['username']}'")
    print(f"1: listed = {cursor.fetchall()[0][0]} - Allows you to be added as a contact (1), or not (0)")
    print("2: Exit and return to main menu")

    inpt = input()
    if inpt == "1":
      value = input("New value of listed (0/1): ")
      cursor.execute(f"UPDATE user_account SET listed = {str(value)} WHERE username = '{client_info['username']}'")
      print(f"Listed has been changed to {value}.")
    elif inpt == "2":
      break
    else:
      print("Unknown option, please try again.")

def make_transaction(source_type, source_name, dest_type, dest_name, money_sent, item_amount=None, refund=None):
  time = int(str(datetime.datetime.now())[:-7].replace('-','').replace(':','').replace(' ',''))

  if source_type == "user" and dest_type == "user":
    # destination transaction
    cursor.execute(f"INSERT INTO transaction (money_gained, source, username, timestamp)\
                     VALUES ({money_sent}, '{source_type}', '{source_name}', {time})")
    dest_id = cursor.lastrowid

    dest_balance = get_balance(dest_type, dest_name) + money_sent
    cursor.execute(f"UPDATE user_account SET balance = {dest_balance} WHERE username = '{dest_name}'")
    dest_transactions = get_list("transactions")
    dest_transactions.append(dest_id)

    cursor.execute(f"UPDATE user_account\
                     SET contacts = '{json.dumps(dest_transactions)}'\
                     WHERE username = '{client_info['username']}'")

    # source transaction
    cursor.execute(f"INSERT INTO transaction (money_gained, source, username, timestamp)\
                         VALUES ({-1*money_sent}, '{dest_type}', '{dest_name}', {time})")
    source_id = cursor.lastrowid

    source_balance = get_balance(source_type, source_name) - money_sent
    cursor.execute(f"UPDATE user_account SET balance = {source_balance} WHERE username = '{source_name}'")
    source_transactions = get_list("transactions")
    source_transactions.append(source_id)

    cursor.execute(f"UPDATE user_account\
                         SET contacts = '{json.dumps(source_transactions)}'\
                         WHERE username = '{client_info['username']}'")

def prompt_send_money():
  print("Choose an account to send money to:")
  inpt = input("Username: ").lower()
  cursor.execute(f"SELECT username FROM user_account WHERE (username = '{inpt}')")
  if len(cursor.fetchall()) > 0:
    return inpt
  print("User not found")
  return None

def send_money(recipient, amount):
  make_transaction(client_info['account_type'], client_info["username"], 'user', recipient, amount)

def prompt_add_contact():
  print("Add contact:")
  inpt = input("Username: ").lower()
  cursor.execute(f"SELECT username FROM user_account WHERE (username = '{inpt}' and listed = 1)")

  if str(cursor.fetchall()) != "[]":
    return inpt
  print("---\nUser not found or is set to private.")
  return None

def add_contact(username):
  current_contacts = get_list("contacts")

  if username in current_contacts:
    print(f"'{username}' is already in your contacts!")
    return
  else:
    print(f"---\nAdded '{username}' as a contact!")

  current_contacts.append(username)

  cursor.execute(f"UPDATE user_account\
                   SET contacts = '{json.dumps(current_contacts)}'\
                   WHERE username = '{client_info['username']}'")
  mydb.commit()

def remove_contact(num):
  current_contacts = get_list("contacts")

  if num < 1 or num > len(current_contacts):
    print(f"Contact #{num} not found.")
    return

  print(f"---Removed '{current_contacts[num-1]}' from your contacts.")
  current_contacts.pop(num-1)

  cursor.execute(f"UPDATE user_account\
                   SET contacts = '{json.dumps(current_contacts)}'\
                   WHERE username = '{client_info['username']}'")

def prompt_create_user_account():
  prompt = {}
  inpt = ""
  print("Create a user account:")
  loop = True
  while loop:
    loop = False
    inpt = input("Username: ")
    if inpt != inpt.lower():
      print(f"Username adjusted: {inpt} -> {inpt.lower()}")
      inpt = inpt.lower()
    cursor.execute("SELECT username FROM user_account")
    for x in cursor.fetchall():
      if inpt == x[0]:
        print(f"The username '{inpt}' is already taken, please choose another username.")
        loop = True

  prompt["username"] = inpt
  inpt = input("Display name: ")
  prompt["name"] = inpt
  inpt = input("Password: ")
  prompt["password"] = inpt

  return prompt

def prompt_create_business_account():
  prompt = {}
  inpt = ""
  print("Create a business account:")
  loop = True
  while loop:
    loop = False
    inpt = input("Business name: ")
    cursor.execute("SELECT business_name FROM business")
    for x in cursor.fetchall():
      if inpt == x[0]:
        print(f"The business name '{inpt}' is already taken, please choose another business name.")
        loop = True
  prompt["business_name"] = inpt

  inpt = input("Password: ")
  prompt["password"] = inpt

  return prompt

def create_user_account(username, name, password):
  cursor.execute(f"INSERT INTO user_account (username, name, password, balance, listed, interest, is_employee)\
                   VALUES ('{username}', '{name}', '{password}', 0, 1, 0.05, 0)")

def create_business_account(business_name, password):
  cursor.execute(f"INSERT INTO business (business_name, password, balance)\
                   VALUES ('{business_name}', '{password}', 0)")

def prompt_user_login():
  print("User Login:")
  while True:
    username = input("Username: ").lower()
    password = input("Password: ")
    cursor.execute(f"SELECT username, password\
                     FROM user_account\
                     WHERE (username = '{username}' AND password = '{password}')")
    if len(cursor.fetchall()) > 0:
      print("Login successful!")
      return username
    print("Invalid login credentials, please try again.")

def prompt_business_login():
  print("Business Login:")
  while True:
    business_name = input("Business name: ")
    password = input("Password: ")
    cursor.execute(f"SELECT business_name, password\
                     FROM business\
                     WHERE (business_name = '{business_name}' AND password = '{password}')")
    if len(cursor.fetchall()) > 0:
      print("Login successful!")
      return business_name
    print("Invalid login credentials, please try again.")

def login(name, account_type):
  global client_info
  client_info['account_type'] = account_type
  if account_type == 'user':
    client_info['username'] = name
  elif account_type == 'business':
    client_info['business_name'] = name

def command(cmd):
  cmd = cmd.lower()
  if cmd == "create_user_account":
    prompt = prompt_create_user_account()
    create_user_account(prompt["username"], prompt["name"], prompt["password"])
    print(f'Account \'{prompt["username"]}\' created successfully.')
    login(prompt["username"], 'user')

  if cmd == "create_business":
    prompt = prompt_create_business_account()
    create_business_account(prompt["business_name"], prompt["password"])
    print(f'Account \'{prompt["business_name"]}\' created successfully.')
    login(prompt["business_name"], 'business')

  if cmd == "user_login":
    prompt = prompt_user_login()
    login(prompt, 'user')

  if cmd == "business_login":
    prompt = prompt_business_login()
    login(prompt, 'business')

  if cmd == "exit":
    print("Have a wonderful day!")
    pass

  if cmd == "notifications":
    pass

  if cmd == "transactions":
    pass

  if cmd == "contacts":
    menu_contacts()
    menu_user_main()

  if cmd == "add_contact":
    prompt = prompt_add_contact()
    if prompt is not None:
      add_contact(prompt)

  if cmd == "remove_contact":
    prompt = input("Remove contact #: ")
    remove_contact(int(prompt))

  if cmd == "send_money":
    prompt = prompt_send_money()
    if prompt is not None:
      print("Input amount to send:")
      amount = round(float(input("Amount: ")), 2)
      send_money(prompt, amount)

  if cmd == "settings":
    change_settings()
    menu_user_main()

  if cmd == "logout":
    global client_info
    client_info = {"account_type": None, "username": None, "business_name": None}
    menu_login()


def menu_login():
  print("\n--- Welcome to Futures Market Bank ---")
  print("Please select an option:")
  print("1: Create a user account")
  print("2: Create a business account")
  print("3: Login to an existing user account")
  print("4: Login to an existing business account")
  print("5: Exit")
  options = {"1": "create_user_account",
             "2": "create_business",
             "3": "user_login",
             "4": "business_login",
             "5": "exit"}

  while True:
    inpt = input()
    if inpt in options:
      command(options[inpt])
      break
    else:
      print("Unknown option, please try again.")
  if client_info["account_type"] == "user":
    menu_user_main()
  elif client_info["account_type"] == "business":
    menu_business_main()

def menu_user_main():
  print(f"\n--- Main Menu: --- Balance: {get_balance('user', client_info['username'])} ---")
  print(f"1: Notifications ({notification_count()})")
  print("2: Transactions")
  print("3: Contacts")
  print("4: Deposit")
  print("5: Send money")
  print("6: Shop businesses")
  print("7: Message user/business")
  print("8: Settings")
  print("9: Logout")
  options = {"1": "notifications",
             "2": "transactions",
             "3": "contacts",
             "4": "deposit",
             "5": "send_money",
             "6": "shop_search",
             "7": "message",
             "8": "settings",
             "9": "logout"}

  while True:
    inpt = input()
    if inpt in options:
      command(options[inpt])
      break
    else:
      print("Unknown option, please try again.")

def menu_business_main():
  pass

def menu_contacts():
  print("--- Contacts ---")
  contacts = get_list("contacts")
  print(contacts)
  print(f"Contacts ({len(contacts)}):")
  i = 0
  while i < len(contacts):
    line = f"{i+1}: {contacts[i]}"
    if len(contacts) > i+1:
      if len(contacts[i]) <= 35 and len(contacts[i+1]) <= 37:
        line = line + ' '*(40-len(line)) + f"{i+2}: {contacts[i+1]}"
        i += 1
    print(line)

    i += 1

  if len(contacts) == 0:
    print("No contacts.")

  options = {"a": "add_contact",
             "r": "remove_contact",
             "m": "message_contact",
             "s": "send_money_contact"}

  while True:
    print("---")
    print("A: Add contact")
    print("R: Remove contact")
    print("M: Message contact")
    print("S: Send money to contact")
    print("E: Exit and return to main menu")

    inpt = input().lower()
    if inpt in options:
      command(options[inpt])
    elif inpt == "e":
      break
    else:
      print("Unknown option, please try again.")

def setup_tables():
  #cursor.execute("DROP TABLE IF EXISTS user_account")
  cursor.execute("CREATE TABLE IF NOT EXISTS user_account(\
                  Username varchar(80) NOT NULL,\
                  name varchar(80) NOT NULL,\
                  password varchar(80) NOT NULL,\
                  balance float NOT NULL,\
                  contacts JSON DEFAULT NULL,\
                  notifications JSON DEFAULT NULL,\
                  listed bool NOT NULL,\
                  transactions JSON DEFAULT NULL,\
                  interest float NOT NULL,\
                  is_employee bool NOT NULL,\
                  weekly_hours_worked float,\
                  hourly_pay float,\
                  Business_name varchar(80),\
                  PRIMARY KEY(Username)\
                  );") # Needs something like CONSTRAINT `brand_id` FOREIGN KEY(`brand_id`) REFERENCES `e_store`.`brands`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE , once other tables are added

  cursor.execute("DROP TABLE IF EXISTS notification")
  cursor.execute("CREATE TABLE IF NOT EXISTS notification(\
                  Notification_id MEDIUMINT NOT NULL AUTO_INCREMENT,\
                  source varchar(16) NOT NULL,\
                  Username varchar(80),\
                  Business_name varchar(80),\
                  type int NOT NULL,\
                  subject varchar(80) NOT NULL,\
                  message varchar(400) NOT NULL,\
                  Refund_id varchar(80),\
                  PRIMARY KEY(Notification_id)\
                  );")

  cursor.execute("DROP TABLE IF EXISTS transaction")
  cursor.execute("CREATE TABLE IF NOT EXISTS transaction(\
                  Transaction_id MEDIUMINT NOT NULL AUTO_INCREMENT,\
                  money_gained float NOT NULL,\
                  source varchar(16) NOT NULL,\
                  Username varchar(80),\
                  Business_name varchar(80),\
                  timestamp BIGINT NOT NULL,\
                  Refund_id MEDIUMINT DEFAULT NULL,\
                  item_amount MEDIUMINT DEFAULT NULL,\
                  PRIMARY KEY(Transaction_id)\
                  );")

  cursor.execute("DROP TABLE IF EXISTS business")
  cursor.execute("CREATE TABLE IF NOT EXISTS business(\
                  Business_name varchar(80) NOT NULL,\
                  password varchar(80) NOT NULL,\
                  notifications JSON DEFAULT NULL,\
                  products JSON DEFAULT NULL,\
                  balance float NOT NULL,\
                  refunds JSON DEFAULT NULL,\
                  employees JSON DEFAULT NULL,\
                  transactions JSON DEFAULT NULL,\
                  sales JSON DEFAULT NULL,\
                  PRIMARY KEY(Business_name)\
                  );")

  cursor.execute("DROP TABLE IF EXISTS sale")
  cursor.execute("CREATE TABLE IF NOT EXISTS sale(\
                  Sale_id MEDIUMINT NOT NULL AUTO_INCREMENT,\
                  Product_id varchar(80) NOT NULL,\
                  discount float NOT NULL,\
                  employee_only bool NOT NULL,\
                  PRIMARY KEY(Sale_id)\
                  );")

  cursor.execute("DROP TABLE IF EXISTS product")
  cursor.execute("CREATE TABLE IF NOT EXISTS product(\
                  Product_id MEDIUMINT NOT NULL AUTO_INCREMENT,\
                  name varchar(80) NOT NULL,\
                  price float NOT NULL,\
                  stock int NOT NULL,\
                  PRIMARY KEY(Product_id)\
                  );")

  cursor.execute("DROP TABLE IF EXISTS refund")
  cursor.execute("CREATE TABLE IF NOT EXISTS refund(\
                    Refund_id MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    Product_id varchar(80) NOT NULL,\
                    price float NOT NULL,\
                    Business_name varchar(80) NOT NULL,\
                    Username varchar(80) NOT NULL,\
                    PRIMARY KEY(Refund_id)\
                    );")

setup_tables()


#cursor.execute(f"UPDATE user_account SET contacts = '{json.dumps([])}' WHERE username = 'dagonw'")

print("users:")
cursor.execute("SELECT * FROM user_account")
for x in cursor.fetchall():
  print(x)
print("businesses:")
cursor.execute("SELECT * FROM business")
for x in cursor.fetchall():
  print(x)

menu_login()

mydb.commit()
'''
cursor.execute("DESC user_account")

for x in cursor:
  print(x)

print("\n")
cursor.execute("DESC notification")

for x in cursor:
  print(x)

print("\n")
cursor.execute("DESC transaction")

for x in cursor:
  print(x)

print("\n")
cursor.execute("DESC business")

for x in cursor:
  print(x)

print("\n")
cursor.execute("DESC sale")

for x in cursor:
  print(x)

print("\n")
cursor.execute("DESC product")

for x in cursor:
  print(x)

print("\n")
cursor.execute("DESC refund")

for x in cursor:
  print(x)
'''

