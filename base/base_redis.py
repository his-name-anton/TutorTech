import json

import redis

class RedisClient:
    def __init__(self, user_id: int, storage: str = 'base', host='localhost', port=6379, db=0):
        self.storage = 'base'
        self.base_path = f'{storage}:user_id:{user_id}:'
        self.redis = redis.Redis(host=host, port=port, db=db)

    def set_value(self, key, value):
        key = self.base_path + key

        if not isinstance(value, (str, float, int, dict, list, set)):
            raise TypeError(f'{value} должен быть типом str | int | float | dict | list | set')

        if isinstance(value, list):
            for item in value:
                self.redis.rpush(key, item)

        if isinstance(value, dict):
            mapping = json.dumps(value)
            self.redis.set(key, mapping)

        if isinstance(value, set):
            value_list = list(value)
            for item in value_list:
                self.redis.sadd(key, item)

        if isinstance(value, (str, int, float)):
            self.redis.set(key, value)


    def get_value(self, key):

        key = self.base_path + key

        type_value = self.redis.type(key).decode('utf-8')

        if type_value == 'set':
            values_set = self.redis.smembers(key)
            return {item.decode('utf-8') for item in values_set}

        if type_value == 'list':
            values_list = self.redis.lrange(key, 0, -1)
            return [item.decode('utf-8') for item in values_list]

        if type_value == 'string':
            value = self.redis.get(key).decode('utf-8')

            if value[0] == '{' and value[-1] == '}':
                print('this dict')
                value_dict = json.loads(value)
                return value_dict

            try:
                value = int(value)
                return value
            except:
                pass

            return value

    def incr_counter(self, key):
        value_now = self.get_value(key)
        value_now += 1
        self.set_value(key, value_now)
        return value_now





class KeysTips(RedisClient):

    STORAGE = 'tips'
    list_tips = 'list_tips'
    counter = 'counter'

    def __init__(self, user_id, *args, **kwargs):
        self.storage = self.STORAGE
        super().__init__(user_id, self.STORAGE, *args, *kwargs)
        self.user_id = user_id


tips_data = KeysTips(user_id=1)