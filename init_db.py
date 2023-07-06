import sqlite3

connection = sqlite3.connect('banco.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO usuario (nome, senha) VALUES (?, ?)",
            ('admin', 'admin123')
            )

connection.commit()
connection.close()