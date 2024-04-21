import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="auto",
  database="mydatabase"
)

cursor = mydb.cursor()