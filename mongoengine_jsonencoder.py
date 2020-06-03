from flask import Flask
from flask.json import JSONEncoder
from bson import json_util
from bson.objectid import ObjectId
import json



class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
       
        return json.JSONEncoder.default(self, o)