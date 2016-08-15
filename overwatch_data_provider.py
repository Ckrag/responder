import sys
import graphgrapper
import utils

# parsed params
# sys.argv[0] contains the requested url
# http://stackoverflow.com/a/30664497

# Print the data you want to return
def main(arg):
    json = str(graphgrapper.GraphGrapper().get_data(utils.Util.get_source_content()))

    response = "jsonpCallback({0})".format(json)

    print(response)

if __name__ == "__main__":
    main(sys.argv[1])