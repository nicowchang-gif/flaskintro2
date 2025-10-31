import mysql.connector

# mydb = mysql.connector.connect(host="localhost", user="root", password = "MySQLPassword")
mydb = mysql.connector.connect(host="localhost", user="root",
	password = "MySQLPassword")

my_cursor = mydb.cursor()
 
# my_cursor.execute("CREATE DATABASE if not exists mysql_flaskintro2")
my_cursor.execute("CREATE DATABASE if not exists mysql_gpdb")

my_cursor.execute("show databases")
for db in my_cursor:
	print(db)
