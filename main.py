import requests
from multiprocessing.dummy import Pool as ThreadPool
import time
import sqlite3
import json
import os.path

class SqlConnector(object):

    db_filename = "responder_db.sqlite"

    #TIMES TABLE
    db_table_name = "response_table"
    #time column
    db_column_time_type = "DECIMAL(19,16)"
    cb_column_time_name = "response_time"
    #timestamp (index)
    cb_column_timestamp_type = "TIMESTAMP"
    cb_column_timestamp_name = "timestamp"

    db_name = "responder_db.sqlite"

    def __init__(self):
        self.create_db_if_needed()

    def api_exists(self, url, db):
        result = db.execute("SELECT id, url FROM apis_table WHERE url=(?)", (url,))

        row_content = result.fetchone()

        if row_content is None:
            return False, None
        return True, row_content

    def create_db_if_needed(self):
        # create file if it doesn't exist
        conn = sqlite3.connect(self.db_filename)
        # make table if it doesn't exist
        self.create_apis_table(conn)

    def add_new_api(self, db, url):
        # Add to apis table
        db.execute("INSERT INTO apis_table(url) VALUES (?)", (url,))

        result = db.execute("SELECT id FROM apis_table WHERE url=(?)", (url,))
        id = str(result.fetchone()[0])

        # Create time table
        db.execute('''CREATE TABLE time_table_''' + id + ''' (
                        timestamp     INT              NOT NULL
                                                       PRIMARY KEY,
                        response_time DECIMAL (24, 20) NOT NULL
                    )''')

        return id


    def add_to_existing_api(self, db, id, response_time):
        current_time = int(time.time())
        db.execute('''INSERT INTO time_table_''' + str(id) + '''(timestamp, response_time)
                    VALUES (?,?)''', (current_time, response_time))
        db.commit()

    def create_apis_table(self, db):
        result = db.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='apis_table'")

        if len(result.fetchall()) == 0:
            db.execute('''CREATE TABLE apis_table (
                id  INTEGER UNIQUE
                            NOT NULL
                            PRIMARY KEY AUTOINCREMENT,
                url TEXT    NOT NULL
            )''')
            db.commit()



    def store_data(self, results):
        db = sqlite3.connect(self.db_name)

        for request_result in results:
            exists, row = (self.api_exists(request_result["url"], db))

            if exists:
                print(request_result["url"] + " existed!")
                self.add_to_existing_api(db, row[0], request_result["time"])
            else:
                print(request_result["url"] + " didn't exist!")
                id = self.add_new_api(db, request_result["url"])
                self.add_to_existing_api(db, id, request_result["time"])

        db.close()




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
            if source[:len(sUri)] != sUri or source[:len(uri)] != uri:
                invalidUris.append(source)

        return invalidUris

    def time_url_opening(self, url):
        pretime = time.time()
        requests.get(url)
        requestTime = time.time() - pretime
        return { "time" : requestTime, "url" : url }

    def get_response_times(self):
        pool = ThreadPool(4)

        results = pool.map(self.time_url_opening, self.urls)
        pool.close()
        pool.join()

        self.db.store_data(results)

    def run(self):
        while True:
            self.get_response_times()
            time.sleep(self.request_frequency_sec)

if __name__ == '__main__':
    Responser()