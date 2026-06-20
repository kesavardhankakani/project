from flask import Flask,request,jsonify
import psycopg2
from datetime import datetime
app = Flask(__name__)
DB_HOST = "localhost"
DB_NAME = "todo"
DB_USER = "postgres"
DB_PASSWORD = "kesava"
def get_db_connection():
    return psycopg2.connect(
        host = DB_HOST,
        database = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD
    )
def create_tasks_table():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        create table IF NOT EXISTS tasks_table(
                id SERIAL PRIMARY KEY,
                task varchar(20) NOT NULL,
                status varchar(20) NOT NULL,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                
                );
""")
    connection.commit()
    cur.close()
    connection.close()
    
create_tasks_table()

@app.route("/post_task" , methods = ['POST'])
def post_task():
    data = request.get_json()
    task = data.get("task")
    status = data.get("status")
    created = data.get("created")
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        insert into tasks_table(task,status,created) values(%s,%s,%s)
""",(task,status,created))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"tasks enterd successfully.."}),200

@app.route("/get_task", methods = ['GET'])
def get_task():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        select *from tasks_table
""")
    data = cur.fetchall()
    tasks = []
    for row in data:
         tasks.append({
              "id":row[0],
              "task":row[1],
              "status":row[2],
              "created":str(row[3])
         })
    connection.commit()
    cur.close()
    connection.close()
    return jsonify(tasks),200

@app.route("/update_task/<int:id>", methods = ['put'])
def update_task(id):
     data = request.get_json()
     task = data.get("task")
     status = data.get("status")
     connection = get_db_connection()
     cur = connection.cursor()
     cur.execute("""
        update tasks_table set task=%s,status=%s where id=%s
""",(task,status,id))
     connection.commit()
     cur.close()
     connection.close()
     return jsonify({"message":"updated successfully.."}),200

@app.route("/delete_task/<int:id>", methods =['delete'])
def delete_task(id):
     connection = get_db_connection()
     cur = connection.cursor()
     cur.execute("""
         delete from tasks_table where id=%s
""",(id,))
     connection.commit()
     cur.close()
     connection.close()
     return jsonify({"message":"deleted successfully.."}),200
     
     

if __name__ == "__main__":
        app.run(debug=True)



 