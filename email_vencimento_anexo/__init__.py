import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import logging
import azure.functions as func
from helpers import connection


def sendMail(mail_content, receiver):
    props = connection.getPropertiesSMTP()
    sender_address = props['username']
    sender_pass = props['password']
    smtp_server = props['smtpServer']
    smtp_port = props['smtpPort']
    
    subject = 'Renovação de Contrato'

    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver
    message['Subject'] = subject

    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))

    #Create SMTP session for sending the mail
    session = smtplib.SMTP(smtp_server, smtp_port) 
    session.starttls() #enable security
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver, text)
    session.quit()


def run():
    engine = create_engine(connection.getPropertiesMysql("adm"))
    Session = sessionmaker(bind=engine)
    session = Session()

    query = """ 
        SELECT 
            email
        FROM 
            pessoa 
        WHERE
            situacao <> "D" 
            and TIMESTAMPDIFF(DAY, DATE(NOW()), JSON_UNQUOTE(JSON_EXTRACT(contrato, CONCAT('$[', IF(JSON_LENGTH(contrato) = 0,'0',JSON_LENGTH(contrato) -1), '].vencimentoAnexoVigente')))) = 30
        """
    query_emails_colaboradores =  session.execute(query)
    resultados = query_emails_colaboradores.fetchall()

    for row in resultados:
        receiver_address = row[0]
        mail_content = ''' 
        <table cellpadding="0" cellspacing="0" width="688" align="center" style="background-color: rgb(255 255 255)";>
                    <tr>
                        <td colspan="2">
                            <a href="https://blueshift.com.br/">
                                <img src="https://blueshift.com.br/internetfiles/emailAdm/001.png" alt="" border="0" style="display:block">
                            </a>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2"
                            style="font:bold 46px calibri;color:#2a2a2a;text-align:center;padding:10px;line-height: 48px">
                            <b style="color:#ff4355;"></b>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2"><img src="https://blueshift.com.br/internetfiles/emailAdm/004.png" alt="" border="0" style="display:block">
                        </td>
                    </tr>
                    <tr">
                        <td colspan="2" style="font:18px arial;color:#515151;text-align:justify;padding-left:30px; padding-right:30px;line-height: 28px" valign="top">
                        <div style="text-align: center;">
                            Prezado(a) colaborador, <br>
                            </div>
                        <div style="text-align: center;">
                            <p>Dentro dos próximos 30 dias você receberá a renovação do seu contrato de prestação de serviços, fique tranquilo, o documento somente é uma formalização da continuidade do contrato e não impede que sejam inseridas alterações após a assinatura.</p>
                            <p>Em caso de dúvidas, fique a vontade para contatar o <b>juridico@blueshift.com.br</b> e a <b>evanildes.vieira@blueshift.com.br</b> para esclarecer dúvidas sobre a renovação. </p><br>
                        </div>
                        </td>
                    </tr>
                    <tr>
                    </tr>
                    <tr>
                        <td colspan="2"><img src="https://blueshift.com.br/internetfiles/emailAdm/007.png" alt="" border="0" style="display:block; margin-top: 20px "></td>
                    </tr>
                </table>
                <table cellpadding="0" cellspacing="0" width="688" align="center">
                    <tr>
                        <td>
                            <a href="https://blueshift.com.br/"><img src="https://blueshift.com.br/internetfiles/emailAdm/012.png" alt="" border="0" style="display:block"></a>
                        </td>
                        <td><a href="https://www.linkedin.com/company/blueshift-brasil/"><img src="https://blueshift.com.br/internetfiles/emailAdm/013.png" alt="" border="0"
                            style="display:block"></a>
                        </td>
                    </tr>
                
                    <tr>
                        <td colspan="2"><img src="https://blueshift.com.br/internetfiles/emailAdm/014.png" alt="" border="0" style="display:block">
                        </td>
                    </tr>
                </table>
    '''
        sendMail(mail_content, receiver_address)


def main(mytimer: func.TimerRequest) -> None:
    run()
