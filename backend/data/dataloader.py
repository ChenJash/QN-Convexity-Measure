import numpy as np
import cmaps
import pickle
import os, random
from IPython import embed
from .datasaver import datasaver
# use saver to save/search user info

class DataLoader(object):
    def __init__(self) -> None:
        self.data = []
        self.data_path = "../datasets/pkg-STL10.pkl"
        self.load_data()
        self.colors = [cmaps.cyclic.colors, cmaps.cosam.colors, cmaps.cosam12.colors, cmaps.amwg.colors, cmaps.GHRSST_anomaly.colors]
        datasaver.set_question_num(self.data["count"])
        self.trans = ["A", "B", "C", "D"]
    
    def get_colors(self, max_label) -> list:
        if max_label < 6:
            return self.colors[0]
        if max_label < 10:
            return self.colors[1]
        if max_label < 12:
            return self.colors[2]
        if max_label < 16:
            return self.colors[3]
        return self.colors[4] # 42 colors

    def load_data(self) -> None:
        with open(self.data_path, "rb") as f:
            self.data = pickle.load(f)
    
    def set_user(self, db, user_id) -> list:
        return datasaver.query_user(db, user_id)

    def hack_data(self) -> dict:
        data = {}
        grids = []
        tmp = list(range(400))
        for _ in range(5):
            grids.append(tmp.copy())
        data["grids"] = grids
        data["labels"] = [0] * 200 + [1] * 200
        cmap = {}
        colors = self.get_colors(2)
        cmap[0] = colors[0].tolist()
        cmap[1] = colors[1].tolist()
        data["colors"] = cmap
        data["index"] = 0
        return data
    
    def get_question(self, db, user_id):
        trans, i = self.set_user(db, user_id)
        return self.data["questions"][trans[i]], i
    
    def get_data(self, db, user_id):
        # load question and data
        raw, pos = self.get_question(db, user_id)
        load_seq = datasaver.load_data(db, raw, user_id)
        data = {}
        data["grids"] = []
        data["grids"].append(raw["grids"][0])
        for i in load_seq:
            data["grids"].append(raw["grids"][i+1])
        data["labels"] = raw["labels"]
        data["index"] = pos
        label_set = set(data["labels"])
        max_label = np.max(np.array(list(label_set)))
        cmap = {}
        colors = self.get_colors(max_label)
        for label in label_set:
            cmap[label] = colors[label].tolist()
        data["colors"] = cmap

        # load history result
        history_result = datasaver.load_history_result(db, raw, user_id)
        for item in history_result:
            item["option"] = self.trans[load_seq.index(item["index"])]
            del item["index"]
        # embed()
        return data, history_result

dataloader = DataLoader()