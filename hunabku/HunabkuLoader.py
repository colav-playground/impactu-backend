from __future__ import print_function
import sys
from pymongo import MongoClient
import pandas as pd
import numpy as np


class HunabkuLoader:
    def __init__(self, dbname='colav',
                 dburi='mongodb://localhost:27017/', dbdrop=False):
        self.dbname = dbname
        self.dbclient = MongoClient(dburi)
        self.db = self.dbclient[self.dbname]
        if dbdrop:
            self.dbclient.drop_database(dbname)

    def check_fields(self, data):
        columns = [
            "journal",
            "publisher",
            "country",
            "article_id",
            "title",
            "author",
            "doi",
            "year",
            "volume",
            "issue",
            "pages",
            "language",
            "abstract"]
        for col in columns:
            if col not in data.keys():
                print('{} not found'.format(col))
                sys.exit(1)

    def load(self, filename, dbcollection, drop=True):
        dbcollection = 'data'
        if filename is None:
            print("Error: file is not provided!", file=sys.stderr)
            sys.exit(1)

        if filename[len(filename) - 4:len(filename)].lower() == ".csv":
            data = pd.read_csv(filename)
            data["_id"] = np.arange(data.shape[0])
            print(data["_id"])
            data = data.to_dict(orient='records')
            self.check_fields(data)
            self.db[dbcollection].insert_many(data)
        elif filename[len(filename) - 5:len(filename)].lower() == ".json":
            data = pd.read_json(filename)
            data["_id"] = np.arange(data.shape[0])
            print(data["_id"])
            self.check_fields(data)
            data = data.to_dict(orient='records')
            self.db[dbcollection].insert_many(data)
        elif filename[len(filename) - 5:len(filename)].lower() == ".xlsx":
            data = pd.read_excel(filename)
            data["_id"] = np.arange(data.shape[0])
            print(data["_id"])
            self.check_fields(data)
            data = data.to_dict(orient='records')
            self.db[dbcollection].insert_many(data)
        else:
            print("file format " + filename[len(filename) - 4:len(filename)].lower() + " not supported", file=sys.stderr)
            sys.exit(1)
