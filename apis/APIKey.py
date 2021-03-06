from mongo.Mongo import MongoDB

# Class to provide API keys to services which can be used to make get call to Google APIs
class APIKey:
    def __init__(self):
        db = MongoDB(database_name='you_search',collection_name='api_keys')
        keys = db.find()
        self.keys = []
        for key in keys:
            self.keys.append(key['key'])
        self.current_key_index=-1

    # Returns the next API key fetched from db. Used when one of the existing keys expires.
    def get_next_key(self):
        self.current_key_index= (self.current_key_index + 1) % len(self.keys)
        return self.keys[self.current_key_index]
