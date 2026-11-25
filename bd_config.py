import pymysql

def conn ():
	return pymysql.connect(
		unix_socket="/var/run/mysqld/mysqld.sock",
		user="app_g3",
		password="SO123",
		database="so_g3_parqueadero",
		autocommit=True
	)


