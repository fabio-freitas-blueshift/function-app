from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pytz
import logging
import azure.functions as func

def run():
    engine = create_engine("mysql+mysqlconnector://usr_clockify_dev@clockifyadmdevblueshift:42Xxor6AFFnV@clockifyadmdevblueshift.mysql.database.azure.com:3306/administrativo_staging2")
    Session = sessionmaker(bind=engine)
    session = Session()
    fuso_horario_sp = pytz.timezone('America/Sao_Paulo')

    # Criar modelo de tabela
    Base = declarative_base()

    class Pessoa(Base):
        __tablename__ = 'pessoa'
        codigo = Column(Integer, primary_key=True)
        situacao = Column(Enum('C', 'D', 'H', 'T'))
        desligamentoAgendamento = Column(Date)
        dataTermino = Column(Date)
        email = Column(String)
        log = Column(JSON)

    # Consultar pessoas com desligamento agendado para hoje.
    hoje = date.today()
    pessoas = session.query(Pessoa).filter(Pessoa.desligamentoAgendamento == hoje).all()
    metadados = []
    array_email = []
    for pessoa in pessoas:
        dados_antigos = {'situacao': pessoa.situacao, 'dataTermino': pessoa.dataTermino.strftime('%Y-%m-%d') if isinstance(pessoa.dataTermino, date) else ""}
        pessoa.situacao = "D"
        pessoa.dataTermino = hoje
        novo_log = {'ip': '::1', 'acao': 'Desativar Colaborador Por Rotina', 'data': datetime.now(fuso_horario_sp).strftime('%Y-%m-%d %H:%M:%S'), 'dados': {'dadosNovos': {'situacao': "D", 'dataTermino': hoje.strftime('%Y-%m-%d')}, 'dadosAntigos': dados_antigos}, 'usuario': 'Rotina Databricks'}
        copia_log = pessoa.log[:]

        if pessoa.log:
            copia_log.append(novo_log)
            pessoa.log = copia_log
        else:
            pessoa.log = [novo_log]

        array_email.append(pessoa.email)

    session.commit()
    session.close()

def main(req: func.HttpRequest) -> func.HttpResponse:
    run()
    return func.HttpResponse(f"Engine Criada com sucesso")
    
