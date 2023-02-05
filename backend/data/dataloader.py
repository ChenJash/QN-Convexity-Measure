import numpy as np
import cmaps
import pickle
import os, random
from IPython import embed
from .datasaver import datasaver
import matplotlib.pyplot as plt
# use saver to save/search user info

class DataLoader(object):
    def __init__(self) -> None:
        self.meta_data = {}
        self.data = []
        self.test_path = "../datasets/pkg-simutest.pkl"
        self.data_path = "../datasets/pkg-ques-20.pkl"
        self.load_data()
        self.colors = [plt.get_cmap('Set1').colors, plt.get_cmap('tab10').colors, plt.get_cmap('Paired').colors, plt.get_cmap('tab20').colors]
        datasaver.set_question_num(self.meta_data["count"])
        self.trans = ["A", "B", "C", "D"]
    
    def get_colors(self, max_label) -> list:
        if max_label < 8:
            return self.colors[0]
        if max_label < 10:
            return self.colors[1]
        if max_label < 12:
            return self.colors[2]
        return self.colors[3]

    def load_data(self) -> None:
        self.data = []
        with open(self.test_path, "rb") as f:
            self.data.append(pickle.load(f))
            self.meta_data["count"] = [self.data[0]["count"]]
        with open(self.data_path, "rb") as f:
            self.data.append(pickle.load(f))
            for ques in self.data[1]["questions"]:
                ques["id"] += self.meta_data["count"][0]
            self.meta_data["count"].append(self.data[1]["count"])
            
    
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
        # return question, part, index
        trans, i = self.set_user(db, user_id)
        part = 0
        target = trans[i]
        if trans[i] < self.meta_data["count"][0]:
            part = 0 
        else:
            part = 1
            target -= self.meta_data["count"][0]
        return self.data[part]["questions"][target], part, i
    
    def get_data(self, db, user_id):
        # load question and data
        raw, part, pos = self.get_question(db, user_id)
        load_seq = datasaver.load_data(db, raw, user_id)
        data = {}
        data["grids"] = []
        for i in load_seq:
            data["grids"].append(raw["grids"][i+part])
        data["labels"] = raw["labels"]
        data["index"] = pos
        label_set = set(data["labels"])
        max_label = np.max(np.array(list(label_set)))
        cmap = {}
        colors = self.get_colors(max_label)
        for label in label_set:
            # cmap[label] = colors[label].tolist()
            cmap[label] = list(colors[label])
        data["colors"] = cmap

        # load history result
        history_result = datasaver.load_history_result(db, raw, user_id)
        for item in history_result:
            item["option"] = self.trans[load_seq.index(item["index"])]
            del item["index"]
        return data, history_result, pos

dataloader = DataLoader()