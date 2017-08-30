import boto3, os
from ConfigParser import SafeConfigParser
from boto3.dynamodb.conditions import Key, Attr
from prettytable import PrettyTable, MSWORD_FRIENDLY



class Lookup:
    def __init__(self):
        self.config_file = os.path.join( os.path.abspath( os.path.dirname( __file__ ) ), "../", '.config.cfg' )
        self.dynamodb = boto3.resource( 'dynamodb' )
        self.parser = SafeConfigParser()
        self.parser.read( self.config_file )
        self.table = self.dynamodb.Table( self.parser.get( 'dynamodb', 'tablename' ) )

    def find_by_message_id(self, id):
        response = self.table.query( KeyConditionExpression=Key( 'messageId' ).eq( id ) )
        t = PrettyTable( ['type', 'messageId', 'source', 'recipient'] )
        for i in response['Items']:
            if i['type'] == 'Bounce' or i['type'] == 'Complaint':
                email_list = []
                for emails in i['recipient']:
                    email_list.append( emails['emailAddress'])
                email_list = [str(r) for r in email_list]
                t.add_row( [i['type'], i['messageId'], i['source'], [email_list]] )
            else:
                email = i['recipient']
                email = [str(r) for r in email]
                t.add_row( [i['type'], i['messageId'], i['source'], [email]] )

        t.align['recipient'] = "l"
        # return t.get_string(fields=['type', 'recipient'])
        return t.get_string()

    # def find_by_recipient(self, email):
    #     response = self.table.query( KeyConditionExpression=Key( 'recipient' ).eq( email ) )




#print(Lookup().find_by_message_id( '0102015e327e6639-dd497187-c32e-4fb4-93bb-21421fab2439-000000' ))
