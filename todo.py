from flask import Flask,request,jsonify
import psycopg2
from datetime import datetime
app = Flask(__name__)
DB_HOST = "localhost"
DB_NAME = "todo"
DB_USER = "postgres"
DB_PASSWORD = "kesava"
#db connection
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
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
""")
    connection.commit()
    cur.close()
    connection.close()
#call function  
create_tasks_table()
#post method
@app.route("/post_task" , methods = ['POST'])
def post_task():
    task = request.json.get("task")
    status = request.json.get("status")
    created = datetime.now()
    updated = datetime.now()
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        insert into tasks_table(task,status) values(%s,%s)
""",(task,status))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"tasks enterd successfully.."}),200
#get method
@app.route("/get_task", methods = ['GET'])
def get_task():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        select * from tasks_table order by id
""")
    data = cur.fetchall()
    tasks = []
    for row in data:
         tasks.append({
              "id":row[0],
              "task":row[1],
              "status":row[2],
              "created":row[3],
              "updated":row[4]
         })
    connection.commit()
    cur.close()
    connection.close()
    return jsonify(tasks),200
#put method
@app.route("/update_task/<int:id>", methods = ['put'])
def update_task(id):
     task = request.json.get("task")
     status = request.json.get("status")
     updated = datetime.now()
     connection = get_db_connection()
     cur = connection.cursor()
     cur.execute("""
        update tasks_table set task=%s,status=%s,updated=%s where id=%s
""",(task,status,updated,id))
     connection.commit()
     cur.close()
     connection.close()
     return jsonify({"message":"updated successfully.."}),200
#delete method
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



 