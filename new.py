from flask import Flask,request,jsonify,render_template
import psycopg2
from flask_bcrypt import Bcrypt
import jwt
import datetime
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

def create_note_table():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        create table IF NOT EXISTS note(noteid SERIAL PRIMARY KEY,
                userid int REFERENCES users_table(userid),
                title varchar(100) NOT NULL,
                description text NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
""")
    connection.commit()
    cur.close()
    connection.close()
     
     
create_users_table()
create_note_table()

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")



SECRET_KEY = "this is my keyy"
def create_jwt(userid,username):
     payload={
          "userid":userid,
          "username":username,
          "exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=10)
     }
     token = jwt.encode(payload,SECRET_KEY,algorithm ="HS256")
     return token

def verify_jwt(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data
    except:
         return None
    
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
                returning userid
""",(username,email,hashed_password,phno,collegename))
    userid = cur.fetchone()[0]
    connection.commit()
    cur.close()
    connection.close()
    token = create_jwt(userid,username)
    return jsonify({"message":"registered successfully",
                    "token":token
                    }),200


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
      userid = user[0]
      if bcrypt.check_password_hash(passwords,password):
            token = create_jwt(userid, username)
            return jsonify({
                  "message":"login successfull",
                  "token":token,
                  "userid":user[0],
                  "username":user[1],
                  "email":user[2],
                  "phno":user[4],
                  "collegename":user[5]
            }),200
      return jsonify({"message":"invalid password"}),200
      
@app.route("/create_note", methods =['POST'])
def create_note():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "token required"}), 401
    user_data = verify_jwt(token)
    if user_data is None:
        return jsonify({"message": "invalid token"}),401
    userid = user_data["userid"]
    username = user_data["username"]
    title = request.json.get("title")
    description = request.json.get("description")
    if not title or not description:
        return jsonify({"message":"all feilds required"}),401
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        insert into note(userid,title,description)values(%s,%s,%s);
""",(userid,title,description))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({
        "message":"note creation successfull",
        "userid":userid,
        "username":username
    }),201

@app.route("/get_note", methods = ['GET'])
def get_note():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message":"token required"}),401
    user_data = verify_jwt(token)
    if user_data is None:
        return jsonify({"message":"invalid token"}),401
    userid = user_data["userid"]
    username = user_data["username"]
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        select*from note where userid =%s
""",(userid,))
    notes =cur.fetchall()
    if not notes:
        cur.close()
        connection.close()
        return jsonify({"message":"no notes found",
                        "userid":userid,
                        "username":username
                        
                        }),401
    note_data = []
    for note in notes:
        note_data.append({
            "noteid":note[0],
            "userid":note[1],
            "title":note[2],
            "description":note[3],
            "created_at":note[4]
        })
        cur.close()
        connection.close()
        return jsonify({
            "message":"your notes is here..",
            "notes":note_data
        }),200
    
@app.route("/update_note/<int:noteid>", methods = ['PUT'])
def update_note(noteid):
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message":"token required"}),401
    user_data = verify_jwt(token)
    if user_data is None:
        return jsonify({"message":"invalid token"}),401
    userid = user_data["userid"]
    username = user_data["username"]
    title = request.json.get("title")
    description = request.json.get("description")
    if not title or not description:
        return jsonify({"message":"all feilds required"}),401

    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        select*from note where noteid=%s AND userid=%s
""",(noteid,userid))
    note = cur.fetchone()
    if note is None:
        cur.close()
        connection.close()
        return jsonify({"message":"note not found"}),401
    cur.execute("""
        update note set title=%s,description=%s where noteid=%s AND userid=%s
""",(title,description,noteid,userid))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"note updated successfully",
                    "note":note
                    })

@app.route("/delete_note/<int:noteid>", methods = ['DELETE'])
def delete_note(noteid):
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message":"token required"}),401
    user_data = verify_jwt(token)
    if user_data is None:
        return jsonify({"message":"invalid token"}),401
    userid = user_data["userid"]

    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        select*from note where noteid=%s AND userid=%s
""",(noteid,userid))
    note = cur.fetchone()
    if not note:
        cur.close()
        connection.close()
        return jsonify({"message":"note not found"}),401
    cur.execute("""
        delete from note where noteid=%s AND userid=%s
""",(noteid,userid))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"note deleted successfully",
                    "note":note
                    }),200

if __name__ == "__main__":
    app.run(debug=True)