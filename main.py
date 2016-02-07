import requests
from multiprocessing.dummy import Pool as ThreadPool
import time
import sqlite3

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
        else:
            return True, row_content

    def create_db_if_needed(self):
        conn = sqlite3.connect(self.db_filename)
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

    urls = ['http://www.yahoo.com']
    request_frequency_sec = 3
    db = SqlConnector()
    #userAgent = 'Your friendly neighborhood API-response-tracker'

    def __init__(self):
        self.run()

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