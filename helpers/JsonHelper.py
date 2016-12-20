import json
from collections import OrderedDict

class JsonHelper:

    def read_file(self, file):
        try:
            fic = open(file)
            data = json.load(fic, object_pairs_hook=OrderedDict)
            return data
        except Exception as e:
            return False
