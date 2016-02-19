import os.path
import json


class Util(object):

    @staticmethod
    def get_source_content():
        template_path = "templates/"
        source_filename = "sources.json"
        source_template_filename = "sources_template.json"

        if os.path.isfile(source_filename):
            with open(source_filename) as source_data:
                sources = json.load(source_data)["sources"]
                if len(sources) > 0:
                    invalid_sources = Util.__get_invalid_sources(sources)
                    if len(invalid_sources) == 0:

                        print("Successfully loaded " + str(len(sources)) + " source(s)")
                        return sources
                    else:
                        print("Found sources, but these sources were invalid: ")
                        for source_string in invalid_sources:
                            print(source_string)
                        print("Please open and correct " + source_filename + " in project root. Remember to add http / https")
                else:
                    print("Found empty source, please append URIs to the sources list inside " + source_filename + " in the project-root-directory")
        else:
            with open(template_path + source_template_filename, 'r') as template:
                source_template = template.read()
                with open(source_filename, 'w') as new_source_file:
                    new_source_file.write(source_template)
            print("Was unable to find " + source_filename + ", created empty source, please append URIs to the sources list inside " + source_filename + " in the project-root-directory")
        return None

    @staticmethod
    def __get_invalid_sources(sources):
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