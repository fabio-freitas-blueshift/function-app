import os

def getPropertiesMysql(database):
    if database == "adm":
        return os.environ["ADM_STRING_CONNECTION"]
    if database == "portal":
        return os.environ["ADM_STRING_CONNECTION"]