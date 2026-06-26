from flask import Flask,request,jsonify
import psycopg2
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
HOST = "localhost"
NAME = "login"
USER = "postgres"
PASSWORD = "kesava"
def get_db_connection():
    return psycopg2.connect(
        host =HOST,
        database=NAME,
        user=USER,
        password=PASSWORD
    )
def create_users_table():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        create table IF NOT EXISTS users_table(userid SERIAL PRIMARY KEY,
                username varchar(100) UNIQUE,
                email varchar(100)UNIQUE,
                password varchar(300)NOT NULL,
                phno varchar(20) NOT NULL,
                collegename varchar(100)NOT NULL                
                );
""")
    connection.commit()
    cur.close()
    connection.close()
create_users_table()
@app.route("/register",methods =['POST'])
def register():
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")
    phno = request.json.get("phno")
    collegename = request.json.get("collegename")
    if not username or not email or not password or not phno or not collegename:       
       return jsonify({"message":"All feilds are required.."}),400
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        select*from users_table where username=%s AND email=%s
""",(username,email))
    exists_user = cur.fetchone()
    if exists_user:
        cur.close()
        connection.close()
        return jsonify({"message":"username,email already exists"})
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    cur.execute("""
    insert into users_table(username,email,password,phno,collegename)values(%s,%s,%s,%s,%s)
""",(username,email,hashed_password,phno,collegename))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"registered successfully"}),200

@app.route("/login", methods = ['post'])
def login():
      username = request.json.get("username")
      email = request.json.get("email")
      password = request.json.get("password")
      if not username or not email or not password:
            return jsonify({"message":"all fields required.."})
      connection = get_db_connection()
      cur = connection.cursor()
      cur.execute("""
          select *from users_table where username=%s AND email=%s
""",(username,email,))
      user = cur.fetchone()
      if user is None:
            cur.close()
            connection.close()
            return jsonify({"messsage":"user not found"})
      passwords = user[3]
      if bcrypt.check_password_hash(passwords,password):
            return jsonify({
                  "message":"login successfull",
                  "userid":user[0],
                  "username":user[1],
                  "email":user[2],
                  "phno":user[4],
                  "collegename":user[5]
            }),200
      return jsonify({"message":"invalid password"}),200
if __name__ == "__main__":
    app.run(debug=True)