import yaml,os,sys
from mashroom.exception import MashroomException


def read_yaml(file_path:str):
    try:
        with open(file_path,'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise MashroomException(sys,e) from e