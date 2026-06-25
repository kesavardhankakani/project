from flask import Flask,request,jsonify
import psycopg2
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta

app =Flask(__name__)
bcrypt = Bcrypt(app)

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "kesava"

def get_db_connection():
    return psycopg2.connect(
        host = DB_HOST,
        database = DB_NAME,
        
        user = DB_USER,
        password = DB_PASSWORD
    )
def create_users_table():
     connection = get_db_connection()
     cur = connection.cursor()
     cur.execute("""
         create table IF NOT EXISTS users(
                 userid SERIAL PRIMARY KEY,
                 username varchar(100) NOT NULL,
                 email varchar(100) UNIQUE,
                 password varchar(300) NOT NULL
                 );
""")
     connection.commit()
     cur.close()
     connection.close()
create_users_table()

@app.route("/signup",methods = ['post'])
def signup():
     username =request.json.get("username")
     email =request.json.get("email")
     password =request.json.get("password")
     if not username or not email or not password:
            return jsonify({"message":"All fields required"}),400
     connection = get_db_connection()
     cur = connection.cursor()
     cur.execute("""
         select *from users where email=%s
""",(email,))
     existing_user = cur.fetchone()
     if existing_user:
           cur.close()
           connection.close()
           return jsonify({"message":"email already exists!!"}),400
     #hashed password
     hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
     cur.execute("""
         insert into users(username,email,password) values(%s,%s,%s)
""",(username,email,hashed_password))
     
     connection.commit()
     cur.close()
     connection.close()
     return jsonify({"message":"signed up successful.."}),200

@app.route("/login", methods = ['post'])
def login():
      email = request.json.get("email")
      password = request.json.get("password")
      if not email or password:
            return jsonify({"message":"all fields required.."})
      connection = get_db_connection()
      cur = connection.cursor()
      cur.execute("""
          select *from users where email=%s
""",(email,))
      user = cur.fetchone()
      cur.close()
      connection.close()
      if user is None:
            return jsonify({"messsage":"user not found"})
      passwords = user[3]
      if bcrypt.check_password_hash(passwords,password):
            return jsonify({
                  "message":"login successfull",
                  "userid":user[0],
                  "username":user[1],
                  "email":user[2]
            }),200
      return jsonify({"message":"invalid password"}),200

      
if __name__ == "__main__":
        app.run(debug=True)
