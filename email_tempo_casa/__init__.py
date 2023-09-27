import logging
import azure.functions as func
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, datetime, timezone
from pytz import timezone
import json
import pandas as pd
from helpers import connection

def getImagesTemplateEmail():
    
    images = {
        "logo" : "https://blueshift.com.br/img-parabenizacoes/aniversario/001.jpg",
        "img" : "https://blueshift.com.br/img-parabenizacoes/aniversario/002.jpg",
        "img2" : "https://blueshift.com.br/img-parabenizacoes/aniversario/003.jpg",
        "barra_azul" : "https://blueshift.com.br/img-parabenizacoes/aniversario/004.jpg",
        "barra_cinza" : "https://blueshift.com.br/img-parabenizacoes/aniversario/005.jpg",
        "botao" : "https://blueshift.com.br/img-parabenizacoes/aniversario/006.jpg",
        "linkedin" : "https://blueshift.com.br/img-parabenizacoes/aniversario/007.jpg",
        "logo2" : "https://blueshift.com.br/img-parabenizacoes/aniversario/008.jpg"
    } 

    return images


def createEmail(row):

    nome = row['nome']
    ano = row['ano']
    anosHoje = row['anosHoje'] 
    s = ''
    
    if(anosHoje > 1):
        s = 's'
    
    # Endereços das imagens para facil manipulação futura

    images = getImagesTemplateEmail()

    logo = images["logo"]
    img = images["img"]
    img2 = images["img2"]
    barra_azul = images["barra_azul"]
    barra_cinza = images["barra_cinza"]
    botao = images["botao"]
    linkedin = images["linkedin"]
    logo2 = images["logo2"]


    # retorna o corpo html montado da pessoa em questão

    return f"""
        <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body>
            <table cellpadding="0" cellspacing="0" width="688px" align="center">
                <thead>
                   <tr>
                       <td colspan="2">
                           <a href="https://blueshift.com.br/"><img src="{logo}" alt="" border="0" style="display:block;">
                           </a>
                       </td>
                   </tr>
                   <tr>
                       <td colspan="2">
                           <img src="{img}" alt="" border="0" style="display:block;">
                       </td>
                   </tr>
                   <tr>
                       <td colspan="2">
                           <img src="{img2}" alt="" border="0" style="display:block;">
                       </td>
                   </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="2" style="font:bold 38px arial; color:#1f1f1f; text-align:center; padding-top:10px; line-height: 46px;">
                            Olá 
                            {nome}
                            hoje você está
                            <br> completando 
                            {anosHoje}
                            ano{s} de <br/>
                            <b style="color:#2cabe0; font-size: 40px; margin: 21px 2; text-align:center;"> BlueShift</b>!
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" style ="padding-top:50px;">
                            <img src="{barra_azul}" style="display:block;">
                            </img>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" style="font:18px arial; color:#515151; text-align:justify; padding-left:50px; padding-right: 50px; line-height: 28px;padding-top:20px;">
                            Um momento
                            <b> incrível </b>
                            e muito importante, são anos de um
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" style="font:18px arial; color:#515151; text-align:justify; padding-left:50px; padding-right: 50px; line-height: 28px;">
                            <b> excelente trabalho</b>
                            dedicados a esta empresa.
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" style="font:18px arial; color:#515151; text-align:justify; padding-left:50px; padding-right: 50px; line-height: 28px;">
                            <br> Você tem dado uma excelente contribuição e
                            <b> somos gratos </b>
                            por seu
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" style="font:18px arial; color:#515151; text-align:justify; padding-left:50px; padding-right: 50px; line-height: 28px;"> 
                            profissionalismo e entrega. Esperamos que você continue aqui por
                            <br> muitos anos!</br>
                        </td>
                    </tr>
                    <tr>
                        <td  colspan="2" style="font:18px arial;color:#515151;text-align:justify;padding-left:50px; padding-right: 50px;line-height: 28px;">
                            <br>
                            <b> Parabéns </b>
                            pelo seu empenho, dedicação e por um trabalho
                            <br>admirável!</br>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" style ="padding-top:20px;">
                            <img src="{barra_cinza}" style="display:block;">
                            </img>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <div style="text-align: center;">
                                <a href="https://blueshift.com.br/">
                            <img src="{botao}" style="display:block;">
                            </img>
                                </a>
                                  </div>
                        </td>
                        <td>
                            <div style ="background:#f8f8f8; border-radius:0px">
                                    <a href="https://br.linkedin.com/company/blueshift-brasil">
                                        <img src="{linkedin}" style="display:block;">
                                        </img>
                                    </a>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" style="align-items: center; justify-content: center;">
                            <div style ="background:#f8f8f8; border-radius:0px;">
                                <div  style="color: #cecece; font-size: 13px; text-align:center;"> © {ano}  BlueShift - Todos os direitos reservados. 
                                </div>
                                <img src="{logo2}" style="display:flex; justify-content: center; align-items: center;  margin: auto;">
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>

    """


def sendEmail(emailContent, row):
    properties = connection.getPropertiesSMTP()
    
    smtpServer = properties["smtpServer"]
    smtpPort = properties["smtpPort"]
    username = properties["username"]
    password = properties["password"]
    
    sender_email = username
    recipient_email = row['email']

    subject = 'Hoje é dia de te parabenizar e agradecer'

    html_content = emailContent

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(emailContent, 'html'))

    session = smtplib.SMTP(smtpServer, smtpPort) 
    session.starttls() #enable security
    session.login(username, password)
    text = message.as_string()
    session.sendmail(username, recipient_email, text)
    session.quit()

def run():
    engine = create_engine(connection.getPropertiesMysql("adm"))
    Session = sessionmaker(bind=engine)
    session = Session()
    query = """
        SELECT 
            nome, 
            email, 
            dataInicio, 
            situacao, 
            YEAR(dataHoraAtual())  AS ano,
            TIMESTAMPDIFF(YEAR, dataInicio, DATE(dataHoraAtual())) AS anosHoje,
            TIMESTAMPDIFF(YEAR,dataInicio,DATE_ADD(DATE(dataHoraAtual()), INTERVAL -1 DAY)) AS anosOntem
        FROM
            pessoa
        WHERE
            situacao IN("H", "T") 
            HAVING
            anosHoje > anosOntem
        """

    query_emails =  session.execute(query)
    resultados = query_emails.fetchall()

    for row in resultados:
        stringMails = row["email"]
        emailContent = createEmail(row)
        sendEmail(emailContent, row)
    

def main(mytimer: func.TimerRequest) -> None:
    run()
