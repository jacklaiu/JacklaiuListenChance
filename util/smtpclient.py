#: encoding: utf8
import requests

class SmtpClient():

    def __init__(self, enable=False):
        self.enable = True

    def sendMail(self, subject, content, receivers='jacklaiu@163.com'):
        if self.enable is False:
            return
        try:
            url = 'http://212.64.7.83:64210/smtpclient/sendHtml?subject=' + subject + '&content=' + content + '&receivers=' + receivers
            print("@@@@@@@@@@@@@->subject: " + subject + " content: " + content)
            requests.get(url)
        except:
            pass
        print('Send!')

s = SmtpClient()
s.sendMail(subject="√DUO RB2001", content="√DUO")