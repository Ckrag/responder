from database import SqlConnector
from utils import Util
import json


class GraphGrapper(object):

    def __init__(self, api_ids = None):

        # Get api info
        self.__apis_info = SqlConnector().get_apis()

        # Builds api ids
        if api_ids is not None:
            self.__ids_to_query = api_ids
        else:
            self.__ids_to_query = []
            for data in self.__apis_info:
                self.__ids_to_query.append(data[0])

    def get_data(self, sources = None):

        # Query data for ids
        data = SqlConnector().get_graph_data(self.__ids_to_query, 40)

        # Builds presentable data
        timestamp_collection = []


        """
        returned format:
        {
            "timestamps" : [
                {
                    "timestamp" : 12345678,
                    "apis_with_respondtime" : [
                        {
                            "url" : "url",
                            "respondtime" : 213214
                        }
                    ]
                }
            ]
        }
        """

        # We can trust that the number of sets returned from the graph_data-query is atleast the number of sets
        # returned from the apis-ids returned from the get_apis query,
        # Since the before mentioned query depends on the later
        unique_timestamps = []
        for index_i, item in enumerate(data):
            # Get unique timestamps
            for index_j, tuple in enumerate(item[1]):
                timestamp = data[index_i][1][index_j][0]
                if timestamp not in unique_timestamps:
                    unique_timestamps.append(timestamp)

        # Build 'timestamps' json-objects
        for index, timestamp in reversed(list(enumerate(unique_timestamps))):
            # For each timestamp, find the responsetime and url of each api, and map it

            apis_with_respondtime = {
                "timestamp" : timestamp,
                "api_responsetimes" : []
            }

            for index_j, api_data in enumerate(data):
                for time_tuple in enumerate(api_data[1]):
                    if time_tuple[1][0] == timestamp:

                        apis_with_respondtime["api_responsetimes"].append(
                            {
                                "index_ref" : self.__apis_info[index_j][0],
                                "response_time" : time_tuple[1][1],
                                "response_code" : time_tuple[1][2]
                            }
                        )

            timestamp_collection.append(apis_with_respondtime)


        api_meta_data = []
        for index, api_info in enumerate(self.__apis_info):
            if sources is not None:
                api_meta_data.append(
                    {
                        "request_url" : api_info[1],
                        "index" : api_info[0],
                        "pretty_name" : sources[index]["pretty_name"],
                        "pretty_color" : sources[index]["pretty_color"]
                    }
                )
            else:
                api_meta_data.append(
                    {
                        "request_url" : api_info[1],
                        "index" : api_info[0]
                    }
                )

        # Present data, return json obj
        return json.dumps({
            "api_data" : timestamp_collection,
            "api_count" : len(data),
            "api_meta_data" : api_meta_data
            #"api_meta" : self.get_meta_data()
        })

    # Extract metadata for raw url, from sources.json
    def get_meta_data(self):
        sources = Util.get_source_content()
        if sources is None:
            return None
