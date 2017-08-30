import boto3

class Utils:
    def __init__(self):
        self.destinations = ['bounce@simulator.amazonses.com', 'complaint@simulator.amazonses.com', 'success@simulator.amazonses.com']

    def send_test_email(self, source):
        ses = boto3.client('ses')
        response = ses.send_email(
            Source=source,
            Destination={
                'ToAddresses': self.destinations
            },
            Message={
                'Subject': {
                    'Data': 'Test Email',
                    'Charset': 'utf-8'
                },
                'Body': {
                    'Text': {
                        'Data': 'TestEmail',
                        'Charset': 'utf-8'
                    },
                 }
             }
            )
        return response


