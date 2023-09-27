import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timezone
import pytz
import logging
import azure.functions as func
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
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
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
                    <td colspan="2" style="font:bold 52px arial;color:#1f1f1f;text-align:center;padding-top:10px;line-height: 48px;">
                    Feliz aniversário<br> {nome} !
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                    <img src="{barra_azul}" alt="" border="0" style="display:block; margin-top:15px;">
                    </td>
                </tr>
                <tr>
                    <td colspan="2" style="font:18px arialcolor:#515151;text-align:justify;padding-left:50px ;padding-right: 50px;line-height: 28px;" valign="top">
                    <br>
                    Achou que íamos esquecer?
                    <br><br>
                    Nós da <b style="color: #2cabe0">BlueShift</b>, desejamos a você um dia maravilhoso, cheio de alegria e harmonia junto de todas as pessoas que você gosta. Que o seu novo ano seja <b>repleto de realizações</b>, conquistas e muito <b>sucesso</b>!
                    <br><br>
                    Obrigado por ser uma parte tão importante desta empresa!
                    <br><br>
                    </td>
                </tr>        
                <tr>
                    <td colspan="2"><img src="{barra_cinza}" alt="" border="0" style="display:block; margin-top: 30px;">
                    </td>
                </tr>
                </tbody>
                <tfoot>
                <tr>
                    <td>
                    <a href="https://blueshift.com.br/">
                        <img src="{botao}" alt="" border="0" style="display:block;">
                    </a>
                    </td>
                    <td>
                    <a href="https://www.linkedin.com/company/blueshift-brasil/">
                        <img src="{linkedin}" alt="" border="0" style="display:block;">
                    </a>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                                <div style ="background:#f8f8f8">
                                    <div  style="color: #cecece; font-size: 13px; text-align:center;"> © {ano}   BlueShift - Todos os direitos reservados. 
                                    </div>
                    <img src="{logo2}" alt="" border="0" style="display:block;">
                                </div>
                    </td>
                </tr>
                </tfoot> 
            </table>
            </body>
        </html>

    """
# COMMAND ----------

def sendEmail(emailContent, row):

    properties = connection.getPropertiesSMTP()
    
    smtpServer = properties["smtpServer"]
    smtpPort = properties["smtpPort"]
    username = properties["username"]
    password = properties["password"]
    sender_email = username
    
    # recipient_email = row['email']
    recipient_email = "fabio.freitas@blueshift.com.br"
    subject = 'Hoje é o seu dia! Feliz aniversário!'

    #html_content = emailContent
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(emailContent, 'html'))

    session = smtplib.SMTP(smtpServer, smtpPort) 
    session.starttls()
    session.login(username, password)
    text = message.as_string()
    session.sendmail(username, recipient_email, text)
    session.quit()

def run():
    fuso_horario_sp = pytz.timezone('America/Sao_Paulo')
    engine = create_engine(connection.getPropertiesMysql("adm"))
    Session = sessionmaker(bind=engine)
    session = Session()
    query_aniversariantes = """
        SELECT 
            nome,
            email,
            dataNascimento,
            YEAR(current_timestamp()) AS ano,
            situacao,
            TIMESTAMPDIFF(YEAR, dataNascimento, current_date()) AS anosHoje,
            TIMESTAMPDIFF(YEAR, dataNascimento, date_add(current_date(), INTERVAL -1 DAY)) AS anosOntem
        FROM pessoa
        WHERE situacao IN("H", "T")
        HAVING
         email IN('aline.sue@blueshift.com.br', 'thais.gomes@blueshift.com.br', 'fabio.freitas@blueshift.com.br')
    """
    query_emails =  session.execute(query_aniversariantes)
    resultados = query_emails.fetchall()
    for linha in resultados:
        stringMails = linha["email"]
        emailContent = createEmail(linha)
        sendEmail(emailContent, linha)


def main(mytimer: func.TimerRequest) -> None:
    run()
    
