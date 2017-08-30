import boto3
import os
from ConfigParser import SafeConfigParser

config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../", '.config.cfg')
lambda_code = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".", 'notification.zip')
parser = SafeConfigParser()
parser.read(config_file)


class Config:
    def __init__(self):

        self.dynamodb = boto3.client( 'dynamodb' )
        self.lambda_client = boto3.client( 'lambda' )
        self.sns = boto3.client( 'sns' )
        self.ses = boto3.client('ses')

    @staticmethod
    def save_config(self, profile):
        with open( config_file, 'w' ) as f:
            parser.write( f )

    @staticmethod
    def backup_config(self):
        print( '[General] Saving config file' )
        with open('.config_backup.cfg', 'w+' ) as b:
            parser.write( b )

    def create_table(self, tablename):
        print( "[DynamoDB] - Creating Table" + str( tablename ) )
        parser.set( 'dynamodb', 'tablename', tablename )
        self.save_config( 'dynamodb' )

        self.dynamodb.create_table(
            TableName=tablename,
            KeySchema=[
                {
                    'KeyType': 'HASH',
                    'AttributeName': 'messageId'
                },
                {
                    'KeyType': 'RANGE',
                    'AttributeName': 'timestamp'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'messageId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    def delete_table(self, tablename):
        print( "[DynamoDB] - Deleting Table " + str( tablename ) )
        response = self.dynamodb.delete_table( TableName=tablename )

    @staticmethod
    def show_config(self):
        for section in parser.sections():
            print("==" * 30)
            for name, value in parser.items(section):
                print( "[%s] %s: %s" % (section, name, value) )
        print("==" * 30)

    def create_lambda(self, exec_role, lambda_name):
        tablename = parser.get( 'dynamodb', 'tablename' )
        print("[Lambda] - Creating Lambda function")
        response = self.lambda_client.create_function(
            FunctionName=lambda_name,
            Runtime='python3.6',
            Role=exec_role,
            Handler='notification.lambda_handler',
            # Code={
            #     'S3Bucket': 'savordel-test',
            #     'S3Key': 'notification.zip'
            # },
            Code={
              'ZipFile': open(lambda_code, 'rb').read()
            },
            Environment={
                'Variables': {
                    'tablename': tablename
                }
            },
            Timeout=5
        )
        arn = response['FunctionArn']
        parser.set( 'lambda', 'exec_role', exec_role )
        parser.set( 'lambda', 'lambda_arn', arn )
        parser.set( 'lambda', 'lambda_name', lambda_name )
        self.save_config( 'lambda' )

    def create_sns_topic(self, topic_name):
        print("[SNS] - Creating SNS Topic")
        response = self.sns.create_topic(
            Name=topic_name
        )
        arn = response['TopicArn']
        parser.set( 'sns', 'sns_arn', arn )
        self.save_config( 'sns' )

    def subscribe_sns_topic(self):
        print("[SNS] - Subscribing SNS to lambda")
        topic_arn = parser.get('sns', 'sns_arn')
        lambda_arn = parser.get('lambda', 'lambda_arn')
        response = self.sns.subscribe(
            TopicArn=topic_arn,
            Protocol='lambda',
            Endpoint=lambda_arn
        )
        self.save_config( 'sns' )

    def lambda_permission(self):
        func_name = parser.get('lambda', 'lambda_name')
        sns_arn = parser.get('sns', 'sns_arn')
        print('[Lambda] - Adding lambda permission')
        response = self.lambda_client.add_permission(
            FunctionName=func_name,
            Action='lambda:*',
            StatementId='snspermissions',
            Principal='sns.amazonaws.com',
            SourceArn=sns_arn,

        )

    def set_ses_notification(self, identity):
        print("[SES] Setting SES Notification for identity " + identity)
        topic_arn = parser.get('sns', 'sns_arn')
        types = ["Bounce", "Complaint", "Delivery"]
        for type in types:
            response = self.ses.set_identity_notification_topic(
                Identity=identity,
                NotificationType=type,
                SnsTopic=topic_arn
            )
        parser.set('ses', 'identity', identity)
        self.save_config('ses')

    def configure(self):
        print("**** SES_LOG Config utility ****")
        identity = raw_input('Enter the SES identity to enable the loggings: ')
        table_name = raw_input('Enter the DynamoDB Table Name to create: ')
        lambda_arn = raw_input('Enter the IAM ARN Role for the lambda function: ')
        lambda_name = raw_input('Enter the Lambda Function Name: ')
        topic_name = raw_input('Enter the SNS Topic Name: ')
        self.create_table(table_name)
        self.create_lambda(exec_role=lambda_arn, lambda_name=lambda_name)
        self.create_sns_topic(topic_name=topic_name)
        self.set_ses_notification(identity=identity)
        self.subscribe_sns_topic()
        self.lambda_permission()

    def delete_resources(self):
        confirmation = raw_input("Are you sure wan't to delete the resources? (yes/no): ")

        if confirmation == "yes":
            self.backup_config()

            # Delete Function
            try:
                lambda_name = parser.get( 'lambda', 'lambda_name' )
                print("[Lambda] Deleting function " + lambda_name)
                response = self.lambda_client.delete_function(
                    FunctionName=lambda_name
                )
                parser.set('lambda', 'lambda_name', '')
                parser.set('lambda', 'lambda_arn', '')
                self.save_config( 'lambda' )
            except:
                print("++++++ [Lambda] Deletion failed " + lambda_name)

                # Delete Table
            try:
                tablename = parser.get( 'dynamodb', 'tablename' )
                print("[Dynamodb] Deleting table " + tablename)
                self.dynamodb.delete_table(
                    TableName=tablename
                )
                parser.set( 'dynamodb', 'tablename', '')
                self.save_config( 'dynamodb' )
            except:
                print( "++++++ [DynamoDB] Deletion failed " + tablename )

            try:
                # Delete SNS
                sns_arn = parser.get( 'sns', 'sns_arn' )
                print("[SNS] Deleting SNS Topic " + sns_arn )
                response = self.sns.delete_topic(
                    TopicArn=sns_arn
                )
                parser.set( 'sns', 'sns_arn', '')
                self.save_config( 'sns' )
            except:
                print( "++++++ [SNS] Deletion failed " + sns_arn )

            # Delete SES
            try:
                identity = parser.get( 'ses', 'identity' )
                print("[SES] Disabling SNS Notification on " + identity )
                types = ["Bounce", "Complaint", "Delivery"]
                for type in types:
                    response = self.ses.set_identity_notification_topic(
                        Identity=identity,
                        NotificationType=type
                    )

                parser.set( 'ses', 'identity', '')
                self.save_config( 'ses' )
            except:
                print( "++++++ [SES] failed to disable notification " + identity )


        elif confirmation == "no":
            print("ok, nothing was changed")
        else:
            print("it's yes|no, nothing else")


