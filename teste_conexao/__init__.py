from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import logging
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        engine = create_engine("mysql+pymysql://usr_clockify_dev@clockifyadmdevblueshift:42Xxor6AFFnV@clockifyadmdevblueshift.mysql.database.azure.com:3306/administrativo_staging2")
        return func.HttpResponse(f"Engine Criada com sucesso")
    except SQLAlchemyError as e:
        return func.HttpResponse(f"Herror, {e}.")
    finally:
        if engine:
            engine.dispose()

    
