import json
import time


class CacheHandler:
    def __init__(self, path_to_cache: str):
        self.path = path_to_cache

    def cache_on_disk(self, local_cache: dict):
        with open(self.path, 'w') as f:
            json.dump(local_cache, f)

    def deserialize(self):
        with open(self.path, 'r') as f:
            data = json.load(f)
            return data

    def check_resources(self, cache: dict):
        # проверяем поле ттл в записях кеша
        # и обновляем если запись устарела
        to_delete = []
        for name in cache:
            print(name)
            print(cache)
            valid_for_sec = cache[name].get("ttl")
            got_at = cache[name].get("reply_time")
            current_time = time.time()
            if current_time >= got_at + valid_for_sec:
                to_delete.append(name)
        for name in to_delete:
            del cache[name]
        self.cache_on_disk(cache)
