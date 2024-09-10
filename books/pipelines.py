import hashlib
import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class MongoPipeline:
    COLLECTION_NAME = "books"

    def __init__(self, mongo_uri, mongo_db):
        """Initializes the pipeline with the MongoDB URI and database
        name"""
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        """Retrieves the MongoDB settings from the settings through the
        crawler."""
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
        )

    def open_spider(self, spider):
        """Opens a connection to MongoDB when the crawler starts."""
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self):
        """Closes the connection to MongoDB when the spider finishes."""
        self.client.close()

    def process_item(self, item, spider):
        """Inserts each scraped item into the MongoDB collection."""
        item_id = self.compute_item_id(item)
        if self.db[self.COLLECTION_NAME].find_one({"_id": item}):
            raise DropItem(f"Duplicate item found: {item}")
        else:
            item["_id"] = item_id
            self.db[self.COLLECTION_NAME].insert_one(ItemAdapter(item).asdict())
            return item

    def compute_item_id(self, item):
        """Computes a unique id for the items in the database"""
        url = item["url"]
        return hashlib.sha256(url.encode("utf-8")).hexdigest()


class BooksPipeline:
    def process_item(self, item, spider):
        return item
