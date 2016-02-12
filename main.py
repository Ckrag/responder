import requests
from multiprocessing.dummy import Pool as ThreadPool
import time
import json
import os.path
from database import SqlConnector


class Responser(object):

    urls = None
    request_frequency_sec = 3
    db = None
    source_filename = "sources.json"
    #userAgent = 'Your friendly neighborhood API-response-tracker'

    def __init__(self):
        if self.init():
            self.run()

    def init(self):
        if os.path.isfile(self.source_filename):
            with open(self.source_filename) as source_data:
                sources = json.load(source_data)["sources"]
                if len(sources) > 0:
                    self.urls = sources

                    invalid_sources = self.get_invalid_sources(self.urls)
                    if len(invalid_sources) == 0:
                        self.db = SqlConnector()
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
            with open(self.source_filename, 'w') as new_source_file:
                new_source_file.write('''{\n  "sources": []\n}''')
            print("Was unable to find " + self.source_filename + ", created empty source, please append URIs to the sources list inside " + self.source_filename + " in the project-root-directory")
        return False

    def get_invalid_sources(self, sources):
        sUri = "https://"
        uri = "http://"
        invalidUris = []

        for source in sources:
            #TODO: This always fails.. I might just be too tired
            if source[:len(sUri)] == sUri or source[:len(uri)] == uri:
                pass
            else:
                invalidUris.append(source)


        return invalidUris

    def time_url_opening(self, url):
        pretime = time.time()
        requests.get(url)
        requestTime = time.time() - pretime
        return { "time" : requestTime, "url" : url }

    def get_response_times(self):
        pool = ThreadPool(4)
        current_time = int(time.time())

        results = pool.map(self.time_url_opening, self.urls)
        pool.close()
        pool.join()

        self.db.store_data(results, current_time)

    def run(self):
        try:
            while True:
                self.get_response_times()
                time.sleep(self.request_frequency_sec)

        except KeyboardInterrupt:
            print("Script stopped, ..exiting")


if __name__ == '__main__':
    Responser()