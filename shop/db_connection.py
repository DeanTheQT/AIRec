import pymongo
from django.conf import settings

# This sets up the client once
client = pymongo.MongoClient(settings.MONGODB_URI)

# Access your specific database
db = client['ecommerce_db']

# Access your collection (like a table)
product_collection = db['products']