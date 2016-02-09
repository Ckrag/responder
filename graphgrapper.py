from database import SqlConnector

# Get api info
apis_info = SqlConnector().get_apis()

# Builds api ids
ids_to_query = []
for data in apis_info:
    ids_to_query.append(data[0])

# Query data for ids
data = SqlConnector().get_graph_data(ids_to_query, 5)

# Builds presentable data
api_data_sets = []

# We can trust that the number of sets returned from the graph_data-query is atleast the number of sets returned from the apis-ids returned from the get_apis query,
# Since the before mentioned query depends on the later
for i in range (0, len(data)):
    #DO THIS
    api_data_sets.append((23232))

# Present data
print(data)