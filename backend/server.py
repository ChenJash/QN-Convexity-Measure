from flask import Flask, jsonify, session, g, request
from data.dataloader import dataloader
from data.datasaver import datasaver
import sqlite3
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(30)
nxt_user_id = 0
finished_ids = []

# for database
DATABASE = "../database/update/database_extra.db"
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/api/init_db")
def init_db():
    datasaver.create_table(get_db())
    return jsonify("Create table successfully.")

@app.route("/api/test_db")
def test_db():
    print(datasaver.insert_user(get_db(), 0))
    print(datasaver.query_user(get_db(), 0))
    return jsonify("Test table successfully.")

@app.route("/api/save_db")
def save_db():
    datasaver.save_results(get_db(), "../database/db.pkl")
    return jsonify("Save table successfully.")

# api for qn
@app.route("/api/login", methods=["POST"])
def login():
    global nxt_user_id
    user_id = session.get("user_id", -1)
    if user_id == -1:
        while nxt_user_id in finished_ids or not datasaver.insert_user(get_db(), nxt_user_id):
            nxt_user_id += 1
        user_id = nxt_user_id
        nxt_user_id += 1
        session["user_id"] = user_id
    finished_num, cur_pos = datasaver.query_user_finish(get_db(), user_id)
    return jsonify({
        "user_id": user_id, 
        "is_first": finished_num < 1, 
        "is_normal": finished_num > datasaver.question_num[0],
        "finish_all": finished_num == datasaver.question_num[0] + datasaver.question_num[1] and finished_num == cur_pos + 1
    })

@app.route("/api/hack-data", methods=["POST"])
def hack_data():
    return jsonify(dataloader.hack_data())

@app.route("/api/get-data", methods=["POST"])
def get_data():
    ret = {}
    user_id = session.get("user_id", -1)
    if user_id == -1:
        ret["msg"] = "Error"
        ret["detail"] = "Please login first"
        return jsonify(ret)
    ret["msg"] = "Success"

    # todo: load current data
    data, history, pos = dataloader.get_data(get_db(), user_id)
    ret["data"] = data
    ret["history"] = history
    ret["cur_pos"] = pos
    ret["total"] = dataloader.meta_data["count"]
    return jsonify(ret)

@app.route("/api/submit", methods=["POST"])
def submit():
    ret = {}
    user_id = session.get("user_id", -1)
    if user_id == -1:
        ret["msg"] = "Error"
        ret["detail"] = "Please login first"
        return jsonify(ret)

    result = request.json["result"]
    db = get_db()
    question, _, _ = dataloader.get_question(db, user_id)
    res = datasaver.submit_result(db, question, user_id, result)
    if res:
        ret["msg"] = "Success"
    else:
        ret["msg"] = "Error"
        ret["detail"] = "No loading infomation!"
    return jsonify(ret)

@app.route("/api/change-question", methods=["POST"])
def change_question():
    ret = {}
    user_id = session.get("user_id", -1)
    if user_id == -1:
        ret["msg"] = "Error"
        ret["detail"] = "Please login first"
        return jsonify(ret)
    
    nxt = request.json["index"]
    res, detail = datasaver.set_user_cur_pos(get_db(), user_id, nxt)
    if res:
        ret["msg"] = "Success"
    else:
        ret["msg"] = "Error"
    ret["detail"] = detail
    return jsonify(ret)

@app.route("/api/get-answer", methods=["POST"])
def get_answer():
    ret = {}
    user_id = session.get("user_id", -1)
    if user_id == -1:
        ret["msg"] = "Error"
        ret["detail"] = "Please login first"
        return jsonify(ret)
    
    res, detail = dataloader.get_answer(get_db(), user_id)
    if not res:
        ret["msg"] = "Error"
        ret["detail"] = detail
        return jsonify(ret)
    ret["msg"] = "Success"
    ret["answer"] = detail
    return jsonify(ret)

@app.route("/api/add-timestamp", methods=["POST"])
def add_timestamp():
    ret = {}
    user_id = session.get("user_id", -1)
    if user_id == -1:
        ret["msg"] = "Error"
        ret["detail"] = "Please login first"
        return jsonify(ret)
    
    datasaver.add_timestamp(get_db(), user_id)
    ret["msg"] = "Success"
    ret["detail"] = "Add time stamp successfully."
    return jsonify(ret)