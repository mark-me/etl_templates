import json

import xmltodict

def xml_to_dict(file_xml: str) -> dict:
    """Converting XML files describing models to Python dictionaries

    Args:
        file_xml (str): The path to a XML file

    Returns:
        dict: The data converted to a dictionary
    """
    # Function not yet used, but candidate for reading XML file
    with open(file_xml) as fd:
        doc = fd.read()
    dict_data = xmltodict.parse(doc)

    return dict_data

def main():
    dict_model_source = xml_to_dict("input/model_source.xml")
    with open('output/model_source.json', 'w') as fp:
        json.dump(dict_model_source, fp, indent=4)
    dict_model_dwh = xml_to_dict("input/model_dwh.xml")
    with open('output/model_dwh.json', 'w') as fp:
        json.dump(dict_model_dwh, fp, indent=4)


if __name__ == "__main__":
    main()