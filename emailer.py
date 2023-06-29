import smtplib
import ssl
from email.message import EmailMessage


class Emailer:
    def __init__(self, receiver_email, readerName):
        self.port = 587  # For starttls
        self.readerName = readerName
        self.smtp_server = "smtp.office365.com"
        self.sender_email = "bot@skrootlab.com"
        self.password = "NRCG23$pam"
        self.foamThresh = 10
        self.context = ssl.create_default_context()
        self.message = EmailMessage()
        self.message['Subject'] = 'Skroot Sensor Alert'
        self.message['From'] = self.sender_email
        self.message['To'] = receiver_email

    def changeReceiver(self, receiver_email):
        del self.message['To']
        self.message['To'] = receiver_email

    def changeMessage(self, message):
        self.message.set_content(message)

    def setMessageFoam(self):
        self.message.set_content(f"""\
        {self.readerName}

        Foam has reached sensor, defoamer should be added.

        Thanks,
        Skroot""")

    def setMessageHarvestClose(self):
        self.message.set_content(f"""\
        {self.readerName}

        Growth is close to being finished, recommended to harvest soon.

        Thanks,
        Skroot""")

    def setMessageHarvestReady(self):
        self.message.set_content(f"""\
        {self.readerName}

        Growth is finished and ready to harvest.

        Thanks,
        Skroot""")

    def sendMessage(self):
        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.ehlo()
            server.starttls(context=self.context)
            server.ehlo()
            server.login(self.sender_email, self.password)
            server.send_message(self.message)
