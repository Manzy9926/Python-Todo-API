from flask import Flask, request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
import pymysql
import os

pymysql.install_as_MySQLdb()

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "your_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "APISEC")

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Ciwonsoko9926$@localhost:3306/APISEC'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'   # matches the table name you created
    Id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {"id": self.Id, "name": self.name, "email": self.email}
    
class Todo(db.Model):
    __tablename__ = 'todo'   # matches the table name you created
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=True)
    done = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    user_id = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {"task_id": self.task_id, "title": self.title, "done": self.done, "date created": self.date_created , "user_id": self.user_id}

@app.route("/todos", methods=["GET"])
def get_todos():
    todos = Todo.query.all()
    return jsonify({"todos": [t.to_dict() for t in todos]})

@app.route("/todos/<int:id>", methods=["GET"])
def get_todo(id):
    todos = Todo.query.get(id)
    if todos:
        return jsonify({"todo":todos.to_dict()})
    else:
        return jsonify({"error": "Todo not found"}), 404    

@app.route("/todos", methods=["POST"])
def post_todo():
    payload = request.get_json()
    if not payload or "title" not in payload:
        return jsonify({"error": "Title is required"}), 400 
    
    new_todo = Todo(
        title=payload["title"],
        done=payload.get("done", False),
        user_id=payload.get("user_id")
    )
    try:
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({"message": "Todo updated successfully", "todo": new_todo.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details":str(e)}), 500  
    
    

@app.route("/todos/<int:id>", methods=["PUT"])
def put_todo(id):
    todo_item = Todo.query.get(id)
    if not todo_item:
        return jsonify({"error": "Todo not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    todo_item.title = data.get("title", todo_item.title)
    if "done" in data:
        todo_item.done = data["done"]
    if "user_id" in data:
        uid = data["User_id"]
        if uid is not None and not User.query.get(uid):
            return jsonify({"error": "User not found"}), 400
        todo_item.user_id = uid

    try:
        db.session.commit()
        return jsonify({"message": "Todo updated successfully", "todo": todo_item.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    
    
    
@app.route("/todos/<int:id>", methods=["DELETE"])
def delete_todo(id):
    todo = Todo.query.get(id)
    if not todo:
        return jsonify({"error": "Todo not found"}), 404
    
    try:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"message": "Todo deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    


@app.before_request
def test_connection():
    try:
        db.session.execute(text('SELECT 1'))
        print("✅ Connected to MySQL successfully!")
    except Exception as e:
        print("❌ Connection failed:", e)


if __name__ == '__main__': 
    app.run(debug=True)