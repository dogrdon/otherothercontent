from pymongo import MongoClient



class MongoConn(object):
	"""Mongo Connection interface"""
	def __init__(self, database, collection):
		super(MongoConn, self).__init__()
		self.database = database
		self.collection = collection
		client = MongoClient()
		self.db = client[database]
		self.collection = self.db[collection]
		
	def save(record):
		self.collection.insert_one(record)

