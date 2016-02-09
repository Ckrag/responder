import sqlite3
import time


class SqlConnector(object):

    db_filename = "responder_db.sqlite"

    def __init__(self):
        self.create_db_if_needed()

    def api_exists(self, url, db):
        result = db.execute("SELECT id, url FROM apis_table WHERE url=(?)", (url,))
        db.close()
        row_content = result.fetchone()

        if row_content is None:
            return False, None
        return True, row_content

    def create_db_if_needed(self):
        # create file if it doesn't exist
        db = sqlite3.connect(self.db_filename)
        # make table if it doesn't exist
        self.create_apis_table(db)
        db.close()

    def add_new_api(self, db, url):
        # Add to apis table
        db.execute("INSERT INTO apis_table(url) VALUES (?)", (url,))

        result = db.execute("SELECT id FROM apis_table WHERE url=(?)", (url,))
        id = str(result.fetchone()[0])

        # Create time table
        db.execute('''CREATE TABLE time_table_''' + id + ''' (
                        timestamp     INT              NOT NULL
                                                       PRIMARY KEY DESC,
                        response_time DECIMAL (24, 20) NOT NULL
                    )''')
        db.close()
        return id


    def add_to_existing_api(self, db, id, response_time):
        current_time = int(time.time())
        db.execute('''INSERT INTO time_table_''' + str(id) + '''(timestamp, response_time)
                    VALUES (?,?)''', (current_time, response_time))
        db.commit()
        db.close()

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


    def get_graph_data(self, ids, limit = None, earliest_time = None):
        db = sqlite3.connect(self.db_filename)
        #ids = db.execute("SELECT * FROM apis_table WHERE ")

        limit_str = ""
        if limit is not None:
            limit_str = "LIMIT " + str(limit)

        results = []
        for id in ids:
            result = db.execute("SELECT timestamp,response_time FROM time_table_" + str(id) + " ORDER BY timestamp desc " + limit_str).fetchall()
            results.append((id, result))
        db.close()
        return results


    def get_apis(self):

        db = sqlite3.connect(self.db_filename)
        result = db.execute("SELECT id, url FROM apis_table").fetchall()
        db.close()
        return result


    def store_data(self, results):

        db = sqlite3.connect(self.db_filename)

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