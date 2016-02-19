import requests
from multiprocessing.dummy import Pool as ThreadPool
import time
import json
import os.path
import datetime
from database import SqlConnector
from socket import error as SocketError
from utils import Util


class Responser(object):

    request_frequency_sec = 3
    db = None
    logging_path = "logging/"
    userAgent = 'Your friendly neighborhood API-response-tracker - https://github.com/ckrag/responder'

    sources_cache = None

    def __init__(self):
        if self.initialize():
            self.run()

    def initialize(self):
        sources = Util.get_source_content()
        if sources is not None:
            self.db = SqlConnector()
            self.sources_cache = sources
            return True
        return False



    def time_url_opening(self, source):
        url = source["url"]
        pretime = time.time()
        try:
            request_result = requests.get(url=url, data=None, headers={'Connection':'close', 'user-agent':self.userAgent})
        except ConnectionError as e:
            self.log_error(e)
            return None
        except SocketError as e:
            self.log_error(e)
            return None

        response_code = request_result.status_code
        request_result.close()
        reques_time = time.time() - pretime
        return { "time" : reques_time, "url" : url, "code" : response_code}


    def format_time(self, time_string):
        if len(time_string) == 0:
            return '0' + time_string
        return time_string

    def get_response_times(self):
        pool = ThreadPool(4)
        current_time = int(time.time())

        results = pool.map(self.time_url_opening, self.sources_cache)

        pool.close()
        pool.join()

        # For now we simply ignore any collections with None values, since None values aren't supported in the database
        if not None in results:
            self.db.store_data(results, current_time)

    def log_error(self, exception):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        with open(self.logging_path + "request_log", 'a') as log_file:
            log_file.write("\n" + timestamp + "\n" + exception + "\n")

    def run(self):
        try:
            while True:
                self.get_response_times()
                time.sleep(self.request_frequency_sec)

        except KeyboardInterrupt:
            print("Script stopped, ..exiting")


if __name__ == '__main__':
    Responser()