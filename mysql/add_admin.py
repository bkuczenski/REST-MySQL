import pymysql
import time
import os
from passlib.hash import bcrypt

def connect_to_db():
    while True:
        try:
            conn = pymysql.connect(host=os.getenv('MYSQL_HOST'), user=os.getenv('MYSQL_ROOT_USER'), 
                                    password=os.getenv('MYSQL_ROOT_PASSWORD'), charset='utf8', db=os.getenv('MYSQL_DB_NAME'))
            cur = conn.cursor()
            break
        except Exception as e:
            print('Database is not up yet...')
            time.sleep(5)

    return cur, conn

def check_if_admin_exists(cur):
    query = """SELECT * FROM `Users` WHERE Email = 'admin'"""
    if cur.execute(query):
        print('Admin user already exists.')
        return True
    else:
        return False

def create_admin(cur, conn):
    adm_query = """SELECT UserTypeId FROM `UserTypes` WHERE UserType = 'admin'"""
    cur.execute(adm_query)
    adm_id = cur.fetchall()[0][0]
    hashed_pass = bcrypt.hash("77DodgeCaymanHedgehog")

    sql = """INSERT INTO `Users` (UserId, Name, Email, HashedPassword, UserType, IsActive) VALUES (default, %s, %s, %s, %s, %s)"""
                                
    cur.execute(sql,('Blackbook Admin', 'admin', hashed_pass, adm_id, 1))
    conn.commit()
    print('Admin user created.')

def main():
    cur, conn = connect_to_db()
    if not check_if_admin_exists(cur):
        create_admin(cur, conn)

if __name__ == '__main__':
    main()
