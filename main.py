import requests
from multiprocessing.dummy import Pool as ThreadPool
import time
import json
import os.path
import datetime
from database import SqlConnector
from socket import error as SocketError


class Responser(object):

    request_frequency_sec = 3
    db = None
    source_filename = "sources.json"
    template_path = "templates/"
    logging_path = "logging/"
    source_template_filename = "sources_template.json"
    userAgent = 'Your friendly neighborhood API-response-tracker - https://github.com/ckrag/responder'

    sources_cache = None

    def __init__(self):
        if self.init():
            self.run()

    def init(self):
        if os.path.isfile(self.source_filename):
            with open(self.source_filename) as source_data:
                sources = json.load(source_data)["sources"]
                if len(sources) > 0:
                    invalid_sources = self.get_invalid_sources(sources)
                    if len(invalid_sources) == 0:
                        self.db = SqlConnector()
                        self.sources_cache = sources
                        print("Successfully loaded " + str(len(sources)) + " source(s)")
                        return True
                    else:
                        print("Found sources, but these sources were invalid: ")
                        for source_string in invalid_sources:
                            print(source_string)
                        print("Please open and correct " + self.source_filename + " in project root. Remember to add http / https")
                else:
                    print("Found empty source, please append URIs to the sources list inside " + self.source_filename + " in the project-root-directory")
        else:
            with open(self.template_path + self.source_template_filename, 'r') as template:
                source_template = template.read()
                with open(self.source_filename, 'w') as new_source_file:
                    new_source_file.write(source_template)
            print("Was unable to find " + self.source_filename + ", created empty source, please append URIs to the sources list inside " + self.source_filename + " in the project-root-directory")
        return False

    def get_invalid_sources(self, sources):
        sUri = "https://"
        uri = "http://"
        invalid_uris = []

        for source in sources:
            source_url = source["url"]
            if source_url[:len(sUri)] == sUri or source_url[:len(uri)] == uri:
                pass
            else:
                invalid_uris.append(source_url)

        return invalid_uris

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