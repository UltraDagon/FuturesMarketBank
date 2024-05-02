import mysql.connector

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
  except Error as err:
    print(f"Error: '{err}'")

  return connection

def setup_tables():
  cursor.execute("DROP TABLE IF EXISTS user_account")
  cursor.execute("CREATE TABLE IF NOT EXISTS user_account(\
                  Username varchar(80) NOT NULL,\
                  name varchar(80) NOT NULL,\
                  password varchar(80) NOT NULL,\
                  balance float NOT NULL,\
                  contacts JSON NOT NULL,\
                  notifications JSON NOT NULL,\
                  listed bool NOT NULL,\
                  transactions JSON NOT NULL,\
                  interest float NOT NULL,\
                  is_employee bool NOT NULL,\
                  weekly_hours_worked float,\
                  hourly_pay float,\
                  Business_name varchar(80),\
                  benefits JSON,\
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
                  business_name varchar(80) NOT NULL,\
                  products JSON NOT NULL,\
                  balance float NOT NULL,\
                  refunds JSON NOT NULL,\
                  employees JSON NOT NULL,\
                  transactions JSON NOT NULL,\
                  PRIMARY KEY(business_name)\
                  );")


mydb = create_server_connection("localhost", "root", "auto", "mydatabase")

cursor = mydb.cursor(buffered=True)
print(mydb.get_server_version())

setup_tables()

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