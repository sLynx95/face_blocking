import requests
import hashlib
from multiprocessing.dummy import Pool

class Api:
    def __init__(self, server_url, pool_size=3):
        self.server_url = server_url
        self.pool = Pool(pool_size)

    def get(self, api, params):
        return requests.get(url=f'{self.server_url}{api}', params=params)

    def run_async(self, task, callback):
        self.pool.apply_async(task, callback=callback)

    def login(self, username, password):
        return self.get('/login', {
            'username': username,
            'password': hashlib.sha256(password.encode('utf-8')).hexdigest()
        })
    
    def get_labels(self, token):
        return self.get('/labels', { 'token': token })

    def get_user_ban_list(self, token):
        return self.get('/user_ban_list', { 'token': token })
