import boto3

import key_config as keys


dynamodb_client = boto3.client(
   'dynamodb',
    aws_access_key_id = 'AKIA5CFUGMGXSSIMGJKI',
    aws_secret_access_key = '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',
    region_name         = 'us-east-1'
    )
dynamodb = boto3.resource(
    'dynamodb',
     aws_access_key_id = 'AKIA5CFUGMGXSSIMGJKI',
     aws_secret_access_key = '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',
     region_name         = 'us-east-1'
    )


def create_table():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table(
       TableName = 'etu_students', # Name of the table
       KeySchema=[
            {
                'AttributeName': 'reg_no',
                'KeyType': 'HASH'  #Partition key
            }
        ],
        AttributeDefinitions=[
             {
                'AttributeName': 'reg_no',
                'AttributeType': 'N'
            }

            ],
	    ProvisionedThroughput={
            
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
            )
    return table