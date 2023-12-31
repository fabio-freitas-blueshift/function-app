import logging
import azure.functions as func
import mysql.connector
import pandas as pd
import smtplib
from sqlalchemy import create_engine
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
from datetime import date, datetime, timezone,timedelta
import pytz
import json
from shutil import copyfile
import os
from helpers import connection
import io

fuso_horario_sp = pytz.timezone('America/Sao_Paulo')

def connMysql(database):    
    mysqlData = connection.getPropertiesMysql(database)
    engine = create_engine(mysqlData)
    conn = engine.connect()
    return conn

def getDataProcedure(query, db):
    conn = connMysql(db)
    result = conn.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    conn.close()
    return df
    

def createEmail():
    date_actual = date.today() - timedelta(days=1)
    msg = f"Relação dos funcionários ativos e em treinamento:{date_actual.strftime('%d/%m/%Y')}"
    ano = date.today().year

    return f"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html>
            <head>
            <meta charset="utf-8">
            </head>
            <body>
               <div style="font-family: Arial; max-width: 100%; width: 100%; margin: auto; background: #fafafa;">
                  <div style="max-width: 560px; width: auto; margin: auto; background: #fff; padding: 10px;">
                    <div style="text-align: center; border-bottom: solid 2px #3f3f3f; padding: 20px 10px;">
                        <img style="width: 240px; height: auto;" src="https://blueshift.com.br/files/img/bluelogo.png">
                    </div>
                  <div style="padding: 70px 20px; color: #3f3f3f">
                     {msg}
                  </div>
                    <div style="padding: 25px 20px; background: #262626; text-align: center; font-size: 14px;">
                        <p style="margin:0; color: #fff;">Esse é um Email Automático. Favor <b>não</b> Responder.</p>
                        <p class="copyright" style="color: #fff; font-size: 12px; margin-top: 5px;">BlueShift | Todos os direitos reservados | {ano} ©</p>
                    </div>
                  </div>
                </div>
            </body>
        </html>

    """

def sendEmail(mail, writer):
    emailContent = createEmail()

    properties = connection.getPropertiesSMTP()
    smtpServer = properties["smtpServer"]
    smtpPort = properties["smtpPort"]
    username = properties["username"]
    password = properties["password"]


    sender_email = username
    #recipient_email = "evanildes.vieira@blueshift.com.br"
    recipient_email = "fabio.freitas@blueshift.com.br"
    subject = 'Relatório diário sistema administrativo'

    html_content = emailContent

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    
    message.attach(MIMEText(emailContent, 'html'))
    date_actual = date.today() - timedelta(days=1)
    newName = f"RelatorioFuncionarios_{date_actual.strftime('%d/%m/%Y')}.xlsx"
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload(writer.getvalue())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="'+newName+'"')
    message.attach(part)

    session = smtplib.SMTP(smtpServer, smtpPort) 
    session.starttls() #enable security
    session.login(username, password)
    text = message.as_string()
    session.sendmail(username, recipient_email, text)
    session.quit()

def run():  
    query = "CALL extracao_evanildes_colaboradores_alocacoes()"
    attachmentDF = getDataProcedure(query, "adm")
    writer = io.BytesIO()
    attachmentDF.to_excel(writer, sheet_name='A1',engine='openpyxl')
    if writer:
        logging.info('correto')
        # listMails = ['evanildes.vieira@blueshift.com.br', 'solange.kato@blueshift.com.br']
        listMails = ['fabio.freitas@blueshift.com.br']
        for row in listMails:
            sendEmail(row, writer)
              
    
def main(mytimer: func.TimerRequest) -> None:
    run()
