from flask import Flask, request, jsonify
import psycopg2

app =Flask(__name__)

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

def create_stu_table():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
                create table  IF NOT EXISTS stu_table(
                stu_id SERIAL PRIMARY KEY,
                stu_name TEXT NOT NULL,
                stu_roll TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE
                );
""")
    connection.commit()
    cur.close()
    connection.close()

create_stu_table()

@app.route("/send_data", methods = ['POST'])
def send_data():
     data = request.get_json()
     stu_name = data.get('stu_name')
     stu_roll = data.get('stu_roll')
     email = data.get('email')
     connection = get_db_connection()
     cur = connection.cursor()
     cur.execute("""
         insert into stu_table(stu_name,stu_roll,email) values(%s,%s,%s)
""",(stu_name,stu_roll,email))
     connection.commit()
     cur.close()
     connection.close()
     return jsonify({"message":"data sended successfully"}),201

@app.route("/get_data", methods = ['GET'])
def get_data():
     connection = get_db_connection()
     cur = connection.cursor()
     cur.execute("""
         select * from stu_table
""")
     data = cur.fetchone()
     cur.close()
     connection.close()
     return jsonify({
          "stu_id":data[0],
          "stu_name":data[1],
          "stu_roll":data[2],
          "email":data[3]
     }),200


@app.route("/update_data", methods = ['PUT'])
def update_data():
     data = request.get_json()
     stu_id = data.get('stu_id')
     stu_name = data.get('stu_name')
     stu_roll = data.get('stu_roll')
     email = data.get('email')
     connection = get_db_connection()
     cur = connection.cursor()
     cur.execute("""
         update stu_table set stu_name=%s,stu_roll=%s,email=%s where stu_id=%s
""",(stu_name,stu_roll,email,stu_id))
     connection.commit()
     cur.close()
     connection.close()
     return jsonify({"message":"data updated successfully"}),200

@app.route("/delete_data", methods = ['DELETE'])
def delete_data():
     data = request.get_json()
     stu_id = data.get('stu_id')
     connection = get_db_connection()
     cur = connection.cursor()
     cur.execute("""
         delete from stu_table where stu_id=%s
""",(stu_id,))
     connection.commit()
     cur.close()
     connection.close()
     return jsonify({"message":"data deletedd successfully"}),200

     

if __name__ == "__main__":
        app.run(debug=True)
