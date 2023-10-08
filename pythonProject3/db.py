import psycopg2

# Подключение к базе данных
connection = psycopg2.connect(user="postgres",
                              password="1234",
                              host="localhost",
                              port="5432",
                              database="Philharmonic")
cursor = connection.cursor()
