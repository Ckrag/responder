from database import SqlConnector


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


    def get_data(self):

        # Query data for ids
        data = SqlConnector().get_graph_data(self.__ids_to_query, 5)

        # Builds presentable data
        apis_list = []

        # We can trust that the number of sets returned from the graph_data-query is atleast the number of sets returned from the apis-ids returned from the get_apis query,
        # Since the before mentioned query depends on the later
        for i in range (0, len(data)):
            api_data = {
                "url" : self.__apis_info[i][1],
                "reponses" : data[i][1]
            }
            apis_list.append(api_data)


        # Present data, return json obj
        return { "api_data" : apis_list }

    def format_json_data(self, data):
        pass