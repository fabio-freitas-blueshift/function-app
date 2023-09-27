import os

def getPropertiesMysql(database):
    if database == "adm":
        return os.environ["ADM_STRING_CONNECTION"]
    if database == "portal":
        return os.environ["ADM_STRING_CONNECTION"]

def getPropertiesSMTP():
    properties = {
        "smtpServer" : "smtp.office365.com",
        "smtpPort" : "587",
        "username" : "sistema-administrativo@blueshift.com.br",
        "password" : "5E1n1QksHtB1"
    }

    return properties