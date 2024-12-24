import json
from pathlib import Path

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


def remove_a_key(d, remove_key):
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key == remove_key:
                del d[key]
            else:
                remove_a_key(d[key], remove_key)
        return d
    elif isinstance(d, list):
        for i in range(len(d)):
            d[i] = remove_a_key(d[i], remove_key)
        return d


def strip_pd_document(file_powerdesigner: str, file_output: str):
    directory = Path("output")
    directory.mkdir(parents=True, exist_ok=True)
    dict_powerdesigner = xml_to_dict(file_powerdesigner)

    # Set new root te dispose of unnecessary data
    dict_model = dict_powerdesigner["Model"]["o:RootObject"]["c:Children"]["o:Model"]

    # Remove redundant JSON sections
    lst_redundant = [
        "c:GeneratedModels",
        "c:GenerationOrigins",
        "c:ExtendedModelDefinitions",
        #"c:LogicalDiagrams",
        #"c:DefaultDiagram",
        "c:DefaultExtendedModelDefinition",
        #"c:TargetModels",
    ]

    # Remove redundant attributes
    dict_model = {
        key: dict_model[key] for key in dict_model if key not in lst_redundant
    }
    dict_model = remove_a_key(dict_model, "a:CreationDate")
    dict_model = remove_a_key(dict_model, "a:ModificationDate")
    dict_model = remove_a_key(dict_model, "a:Creator")
    dict_model = remove_a_key(dict_model, "a:Modifier")
    dict_model = remove_a_key(dict_model, "a:History")

    with open("output/" + file_output, "w") as fp:
        json.dump(dict_model, fp, indent=4)


def main():
    directory = Path("output")
    directory.mkdir(parents=True, exist_ok=True)
    dict_model_source = xml_to_dict("input/model_source.xml")
    with open("output/model_source.json", "w") as fp:
        json.dump(dict_model_source, fp, indent=4)
    dict_model_dwh = xml_to_dict("input/model_dwh.xml")
    with open("output/model_dwh.json", "w") as fp:
        json.dump(dict_model_dwh, fp, indent=4)


if __name__ == "__main__":
    # main()
    strip_pd_document(file_powerdesigner="input/ExampleDWH.ldm", file_output="example_dwh.json")
    strip_pd_document(file_powerdesigner="input/ExampleSource.ldm", file_output="example_source.json")
