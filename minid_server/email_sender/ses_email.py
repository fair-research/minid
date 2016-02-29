import boto.ses

class SESEmail:

    def __init__(self, app):

        self.conn = boto.ses.connect_to_region('us-east-1',
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])

    def send_email(self, address, code):
        print "Sending %s to %s" % (code, address)
        self. conn.send_email(
            'info@minid.bd2k.org',
            'Minid registration code',
            'Your minid registration code is: %s\n\nCopy this code and put it in your minid configuration file.' % code,
        [address])
