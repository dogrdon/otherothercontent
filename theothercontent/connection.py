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
		
	def save_record(self, record):
		# save one document
		self.collection.insert_one(record)

	def save_records(self, records):
		# save one or more documents
		self.collection.insert_many(records)
