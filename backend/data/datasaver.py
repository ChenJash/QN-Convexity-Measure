import sqlite3, random, time, pickle
from IPython import embed

class DataSaver(object):
    def __init__(self) -> None:
        self.insert_user_query = "INSERT INTO user(user_session, qualified, cur_pos, finished_num, _order) VALUES(?, ?, ?, ?, ?);"
        self.select_user_query = "SELECT * FROM user WHERE user_session = {};"
        self.select_user_qualified_query = "SELECT qualified FROM user WHERE user_session = {};"
        self.update_user_qualified_query = "UPDATE user SET qualified = {} WHERE user_session = {};"
        self.insert_load_query = "INSERT INTO load(user_session, question_id, question_name, load_seq) VALUES(?, ?, ?, ?);"
        self.select_user_finished_num_query = "SELECT finished_num FROM user WHERE user_session = {}"
        self.update_user_finished_num_query = "UPDATE user SET finished_num = {} WHERE user_session = {}"
        self.update_user_cur_pos_query = "UPDATE user SET cur_pos = {} WHERE user_session = {}"
        self.select_load_query = "SELECT * FROM load WHERE user_session = {} AND question_id = {};"
        self.update_load_query = "UPDATE load SET load_seq = '{}' WHERE user_session = {} AND question_id = {};"
        self.insert_submit_query = """INSERT INTO submit(user_session, question_id, question_name, submit_date, 
                                rank_T, rank_S, rank_E, rank_C, colors) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        self.select_submit_query = "SELECT * FROM submit WHERE user_session = {} AND question_id = {};"
        self.select_result_query = "SELECT submit_date, rank_T, rank_S, rank_E, rank_C, colors FROM submit WHERE user_session = {} AND question_id = {};"
        self.select_all_results = "SELECT user_session, question_id, question_name, submit_date, rank_T, rank_S, rank_E, rank_C FROM submit;"
        self.question_num = []
        self.sequence = ["T", "S", "E", "C"]
        self.trans = {"A": 0, "B": 1, "C": 2, "D": 3}
        self.trans2 = {"T": 0, "S": 1, "E": 2, "C": 3}
    
    def set_question_num(self, num: int) -> None:
        self.question_num = num
    
    def create_table(self, db: sqlite3.Connection) -> None:
        cur = db.cursor()
        cur.execute("CREATE TABLE user(user_session integer primary key, qualified integer not null, cur_pos integer not null, finished_num integer not null, _order text not null);")
        cur.execute("CREATE TABLE load(load_id integer primary key autoincrement, question_id integer not null, question_name text not null, user_session integer not null, load_seq text not null, foreign key(user_session) references user(user_session));")
        cur.execute("""CREATE TABLE submit(submit_id integer primary key autoincrement, 
                question_id integer not null, question_name text not null, submit_date real not null,
                rank_T int not null, rank_E int not null, rank_C int not null, rank_S int not null,
                colors text not null, user_session integer not null, foreign key(user_session) references user(user_session));
        """)
        db.commit()
    
    def insert_user(self, db: sqlite3.Connection, session_id) -> bool:
        _, pos = self.query_user(db, session_id)
        if pos == -1:
            cur = db.cursor()
            seq0 = list(range(self.question_num[0]))
            random.shuffle(seq0)
            seq1 = list(map(lambda x: x+self.question_num[0], list(range(self.question_num[1]))))
            random.shuffle(seq1)
            seq = seq0 + seq1
            cur.execute(self.insert_user_query, (session_id, 0, 0, 0, ",".join(list(map(str, seq)))))
            db.commit()
            return True
        return False
    
    def query_user(self, db: sqlite3.Connection, session_id):
        cur = db.cursor()
        cur.execute(self.select_user_query.format(session_id))
        rows = cur.fetchall()
        if len(rows) > 0:
            seq = rows[0][4]
            return list(map(int, seq.split(","))), rows[0][2]
        return [], -1

    def load_data(self, db: sqlite3.Connection, question, session_id) -> list:
        cur = db.cursor()
        load_seq = list(range(4))
        random.shuffle(load_seq)
        seq_str = "".join(list(map(lambda x: self.sequence[x], load_seq)))
        cur.execute(self.select_load_query.format(session_id, question["id"]))
        rows = cur.fetchall()
        if len(rows) > 0:
            seq_str = rows[0][-1]
            load_seq = list(map(lambda x:self.trans2[x], seq_str))
        else:
            cur.execute(self.insert_load_query, (session_id, question["id"], question["name"], seq_str))
        db.commit()
        return load_seq
    
    def submit_result(self, db: sqlite3.Connection, question, session_id, result) -> bool:
        cur = db.cursor()
        # query load if without load return False
        cur.execute(self.select_load_query.format(session_id, question["id"]))
        rows = cur.fetchall()
        if len(rows) == 0:
            return False
        load_seq = rows[0][-1]

        # query submit judge if first finish question
        cur.execute(self.select_submit_query.format(session_id, question["id"]))
        rows = cur.fetchall()
        if len(rows) == 0:
            cur.execute(self.select_user_finished_num_query.format(session_id))
            finished_num = cur.fetchall()[0][0]
            cur.execute(self.update_user_finished_num_query.format(finished_num + 1 ,session_id))

        rank_tsec = [4, 4, 4, 4]
        color_tsec = ['/', '/', '/', '/']
        rank = 0
        for i in range(len(result)):
            item = result[i]
            option = self.trans[item['option']]
            grid_type = load_seq[option]
            if i > 0 and item['equal'][0] and result[i-1]['equal'][1]:
                rank -= 1
            rank_tsec[self.trans2[grid_type]] = rank
            color_tsec[self.trans2[grid_type]] = item['color']
            rank += 1
        color_str = ",".join(color_tsec) 
        cur.execute(self.insert_submit_query, (session_id, question["id"], question["name"], time.time(),
            rank_tsec[0], rank_tsec[1], rank_tsec[2], rank_tsec[3], color_str))
        db.commit()
        return True
    
    def load_history_result(self, db: sqlite3.Connection, question, session_id) -> list:
        history_result = []
        cur = db.cursor()
        cur.execute(self.select_result_query.format(session_id, question["id"]))
        rows = cur.fetchall()
        if len(rows) == 0:
            return history_result
        rows.sort(key=lambda x: x[0], reverse=True)
        row = rows[0]
        color_str = row[-1]
        color_tsec = color_str.split(",")
        rank_tsec = [row[1], row[2], row[3], row[4]]
        for i in range(4):
            if rank_tsec[i] == 4:
                continue
            history_result.append({
                "index": i,
                "rank": rank_tsec[i],
                "color": color_tsec[i],
                "equal": [False, False]
            })
        history_result.sort(key=lambda x: x["rank"] * 10 + i)
        for i in range(len(history_result) - 1):
            if history_result[i]["rank"] == history_result[i+1]["rank"]:
                history_result[i]["equal"][1] = True
                history_result[i+1]["equal"][0] = True
        return history_result

    def set_user_cur_pos(self, db: sqlite3.Connection, session_id, pos):
        if pos < 0:
            return False, "Target position out of range."
        if pos >= self.question_num[0] + self.question_num[1]:
            return False, "This is the final question."
        if pos >= self.question_num[0]:
            judge, detail = self.judge_test(db, session_id)
            if not judge:
                return judge, detail
        cur = db.cursor()
        cur.execute(self.update_user_cur_pos_query.format(pos, session_id))
        db.commit()
        return True, "Successfully change pos."
    
    def save_results(self, db: sqlite3.Connection, save_path: str) -> None:
        cur = db.cursor()
        cur.execute(self.select_all_results)
        rows = cur.fetchall()
        with open(save_path, "wb") as f:
            pickle.dump(rows, f)

    def judge_test(self, db: sqlite3.Connection, session_id):
        cur = db.cursor()
        cur.execute(self.select_user_qualified_query.format(session_id))
        rows = cur.fetchall()
        if rows[0][0] == 1:
            return True, "Has passed simulation test."
        # judge simu test
        trans, _ = self.query_user(db, session_id)
        wrong_num = 0
        for id in range(self.question_num[0]):
            cur.execute(self.select_result_query.format(session_id, trans[id]))
            rows = cur.fetchall()
            if len(rows) == 0:
                return False, "Test question [{}]: the question has not been answered.".format(id+1)
            rows.sort(key=lambda x: x[0], reverse=True)
            row = rows[0]
            if row[4] > 0 or row[3] != 1:
                wrong_num += 1
                # if wrong_num > 1:
                #     return False, "Test question [{}]: the answer given is wrong.".format(id+1)
        cur.execute(self.update_user_qualified_query.format(1, session_id))
        db.commit()
        return True, "Pass simulation test."
datasaver = DataSaver()