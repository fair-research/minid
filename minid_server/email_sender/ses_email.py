import boto3


class SESEmail:

    def __init__(self, app):

        self.app = app

        self.client = boto3.client(
            'ses',
            region_name=app.config.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])

    def send_email(self, address, code):
        self.client.send_email(
            Source=self.app.config['AWS_EMAIL_SENDER'],
            Destination={
                'ToAddresses': [address],
            },
            Message={
                'Subject': {
                    'Data': 'Minid registration code',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data':
                            'Your minid registration code is: %s\n\n'
                            'Copy this code and put it in your minid '
                            'configuration file.' % code,
                        'Charset': 'UTF-8'

                    }
                }
            },
        )
