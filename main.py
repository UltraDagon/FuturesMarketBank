import mysql.connector

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

def get_contacts():
  cursor.execute(f"SELECT contacts FROM user_account WHERE (username = '{client_info['username']}')")

  if cursor.fetchall()[0][0] is None:
    return []
  return cursor.fetchall()[0]

def change_settings():
  print("--- Settings ---") # Will change 0 to reflect listed's value for the current user
  print(f"1: listed = {0} - Allows you to be added as a contact (1), or not (0)")
  print("2: Exit and return to main menu")
  options = {"1": "listed"}
  while True:
    inpt = input()
    if inpt == "1":
      value = input("New value of listed (0/1): ")
      cursor.execute(f"UPDATE user_account SET listed = {value} WHERE username = '{client_info['username']}'")
    elif inpt == "2":
      break
    else:
      print("Unknown option, please try again.")

def prompt_add_contact():
  print("Add contact:")
  inpt = input("Username: ").lower()
  cursor.execute(f"SELECT username FROM user_account WHERE (username = '{inpt}' and listed = 1)")
  if cursor.fetchall()[0][0] is not None:
    return inpt
  print("User not found or is set to private.")
  return None

def add_contact(username):
  pass

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

  if cmd == "notifications":
    pass

  if cmd == "transactions":
    pass

  if cmd == "contacts":
    menu_contacts()
    menu_user_main()

  if cmd == "add_contact":
    prompt = prompt_add_contact()
    add_contact(prompt)

  if cmd == "settings":
    change_settings()
    menu_user_main()

def menu_login():
  print("\n--- Welcome to Futures Market Bank ---")
  print("Please select an option:")
  print("1: Create a user account")
  print("2: Create a business account")
  print("3: Login to an existing user account")
  print("4: Login to an existing business account")
  options = {"1": "create_user_account",
             "2": "create_business",
             "3": "user_login",
             "4": "business_login"}

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
  print("\n--- Main Menu: ---")
  print(f"1: Notifications ({notification_count()})")
  print("2: Transactions")
  print("3: Contacts")
  print("4: Shop businesses")
  print("5: Send money")
  print("6: Message user/business")
  print("7: Settings")
  print("8: Logout")
  options = {"1": "notifications",
             "2": "transactions",
             "3": "contacts",
             "4": "shop_search",
             "5": "send_money",
             "6": "message",
             "7": "settings",
             "8": "logout"}

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
  contacts = get_contacts()
  print(f"Contacts ({len(contacts)}):")
  for i in range(len(contacts)):
    line = f"{i}: {contacts[i]}"
    if len(contacts) > i+1:
      if len(contacts[i]) <= 35 and len(contacts[i+1]) <= 37:
        line += line + ' '*(40-len(line)) + f"{i+1}: {contacts[i+1]}"
        i += 1
    print(line)

  if len(contacts) == 0:
    print("No contacts.")

  print("---")
  print("A: Add contact")
  print("R: Remove contact")
  print("M: Message contact")
  print("S: Send money to contact")
  print("E: Exit and return to main menu")
  options = {"A": "add_contact",
             "R": "remove_contact",
             "M": "message_contact",
             "S": "send_money_contact",
             "E": ""}

  while True:
    inpt = input()
    if inpt in options:
      command(options[inpt])
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
                  Notification_id varchar(80) NOT NULL,\
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
                  Transaction_id varchar(80) NOT NULL,\
                  money_gained float NOT NULL,\
                  source varchar(16) NOT NULL,\
                  Username varchar(80),\
                  Business_name varchar(80),\
                  timestamp int NOT NULL,\
                  Refund_id varchar(80) NOT NULL,\
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
                  Sale_id varchar(80) NOT NULL,\
                  Product_id varchar(80) NOT NULL,\
                  discount float NOT NULL,\
                  employee_only bool NOT NULL,\
                  PRIMARY KEY(Sale_id)\
                  );")

  cursor.execute("DROP TABLE IF EXISTS product")
  cursor.execute("CREATE TABLE IF NOT EXISTS product(\
                  Product_id varchar(80) NOT NULL,\
                  name varchar(80) NOT NULL,\
                  price float NOT NULL,\
                  stock int NOT NULL,\
                  PRIMARY KEY(Product_id)\
                  );")

  cursor.execute("DROP TABLE IF EXISTS refund")
  cursor.execute("CREATE TABLE IF NOT EXISTS refund(\
                    Refund_id varchar(80) NOT NULL,\
                    Product_id varchar(80) NOT NULL,\
                    price float NOT NULL,\
                    Business_name varchar(80) NOT NULL,\
                    Username varchar(80) NOT NULL,\
                    PRIMARY KEY(Refund_id)\
                    );")

#setup_tables()

print("users:")
cursor.execute("SELECT * FROM user_account")
for x in cursor.fetchall():
  print(x)
print("businesses:")
cursor.execute("SELECT * FROM business")
for x in cursor.fetchall():
  print(x)

menu_login()

print(client_info)
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

