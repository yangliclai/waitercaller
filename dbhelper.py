import pymongo
from bson.objectid import ObjectId

DATABASE = "waitercaller"


class DBHelper:

    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client[DATABASE]

    def get_user(self, email):
        return self.db.users.find_one({"email": email})

    def add_user(self, email, salt, hashed):
        self.db.users.insert({"email": email, "salt": salt, "hashed": hashed})

    def add_table(self, number, owner):
        new_id = self.db.tables.insert({"number": number, "owner": owner})
        return new_id

    def update_table(self, _id, url):
        self.db.tables.update({"_id": _id}, {"$set": {"url": url}})

    def get_tables(self, owner_id):
        return list(self.db.tables.find({"owner": owner_id}))

    def get_table(self, table_id):
        return self.db.tables.find_one({"_id": ObjectId(table_id)})

    def delete_table(self, table_id):
        self.db.tables.remove({"_id": ObjectId(table_id)})

    def add_request(self, table_id, time,count):
        table = self.get_table(table_id)
        try:
            new_id = self.db.requests.insert({"owner": table['owner'], "table_number": table[
                                    'number'], "table_id": table_id, "time": time,"count":count})
            return new_id
        except pymongo.errors.DuplicateKeyError:
            return False

    def update_request(self, _id, count):
        self.db.requests.update({"_id": _id}, {"$set": {"count": count}})

    def add_table_fulltest(self, number, owner,url):
        new_id02 = self.db.tables.insert({"number": str(int(number) + 1), "owner": owner,"url": url})
        return new_id02

    def delete_table_fulltest(self, table_id):
        table02 = self.get_table(table_id)
        self.db.tables.remove({"owner": table02['owner'], "number": table02['number']})

    def delete_request_redundancy(self, table_id):
        table03 = self.get_table(table_id)
        self.db.requests.remove({"owner": table03['owner'],"table_number": table03['number']})

    def get_requests(self, owner_id):
        return list(self.db.requests.find({"owner": owner_id}))

    def get_request(self, requestid):
        return self.db.requests.find_one({"_id": ObjectId(requestid)})

    def get_requestcount_max(self, owner_id):
        maxcount = self.db.requests.find({"owner": owner_id}).sort(["count",-1]).limit(1)
        return maxcount['count']

    def delete_request(self, request_id):
        self.db.requests.remove({"_id": ObjectId(request_id)})