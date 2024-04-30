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
                  balance int NOT NULL,\
                  contacts JSON NOT NULL,\
                  notifications JSON NOT NULL,\
                  listed bool NOT NULL,\
                  transactions JSON NOT NULL,\
                  interest float NOT NULL,\
                  is_employee bool NOT NULL,\
                  weekly_hours_worked float,\
                  hourly_pay float,\
                  Business_name varchar(80),\
                  PRIMARY KEY(Username)\
                  );") # Needs something like CONSTRAINT `brand_id` FOREIGN KEY(`brand_id`) REFERENCES `e_store`.`brands`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE , once other tables are added


mydb = create_server_connection("localhost", "root", "auto", "mydatabase")

cursor = mydb.cursor(buffered=True)
print(mydb.get_server_version())

setup_tables()

cursor.execute("DESC user_account")

for x in cursor:
  print(x)