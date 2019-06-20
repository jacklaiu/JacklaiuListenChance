#: encoding: utf8
import requests

class SmtpClient():

    def __init__(self, enable=False):
        self.enable = True

    def sendMail(self, subject, content, receivers='jacklaiuwx@qq.com'):
        if self.enable is False:
            return
        try:
            url = 'http://182.61.17.54:64210/smtpclient/sendHtml?subject=' + subject + '&content=' + content + '&receivers=' + receivers
            #print("@@@@@@@@@@@@@->subject: " + subject + " content: " + content)
            ret = requests.get(url)
            print(ret)
        except:
            pass
        #print('Send!')

# s = SmtpClient()
# s.sendMail(subject="√DUO RB2001", content="√DUO")