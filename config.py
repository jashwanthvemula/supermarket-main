import mysql.connector

class Config:
    domain = 'supermarket.com'
    smtp_username = ""
    smtp_password = ""
    db_host = '127.0.0.1'
    user = 'root'
    password = 'new_password'  # Change this to your actual MySQL password
    database = 'supermarketdb'

    @classmethod
    def get_domain(cls):
        return cls.domain