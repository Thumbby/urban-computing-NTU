import pymongo


class MongoDBLink(object):
    def __init__(self,database_name,host='127.0.0.1', port=27017):
        # connect mongodb
        self.host = host
        self.port = port
        self.client = pymongo.MongoClient(host=self.host, port=self.port)
        #
        self.db = self.client[database_name]
        # self.db = self.client.get_database('db_name')
        # self.db = self.client.db_name

    # add records mongo_py.add_one({'name': 'abc', 'x_value': 88})
    def add_one(self,collection,data):
        result = self.db[collection].insert_one(data)
        # return inserted_id
        print(result.inserted_id)
