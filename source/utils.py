import boto3

class Utils:
    def send_test_email(self, source, destination):
        ses = boto3.client('ses')
        response = ses.send_email(
            Source=source,
            Destination={
                'ToAddresses': [destination]
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

