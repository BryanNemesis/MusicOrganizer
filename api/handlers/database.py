import json

import boto3
from boto3.dynamodb.conditions import Key


db = boto3.resource('dynamodb', endpoint_url="http://db-local:8000", region_name="eu-west-1")
collections = db.Table(name='collections')
        

def get_collection_list(user_id: str):
    response = collections.query(KeyConditionExpression=Key('user_id').eq(user_id))
    return response


def get_collection_detail(user_id: str, collection_title: str):
    response = collections.get_item(
        Key={
            'user_id': user_id,
            'title': collection_title
            }
        )
    return response


def create_collection(user_id: str, collection):
    response = collections.put_item(Item=collection)
    return response


def add_album_to_collection(user_id: str, collection_title, album):
    response = collections.update_item(
        Key={
            'user_id': user_id,
            'title': collection_title
            },
        UpdateExpression='SET albums = list_append(albums, :album)',
        ExpressionAttributeValues = {
            ':album': [album]
        },
        ReturnValues="UPDATED_NEW"
        )
    return response


def create_collections_table():
    table = db.create_table(
        TableName='collections',
        KeySchema=[
            {
                'AttributeName': 'user_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'title',
                'KeyType': 'RANGE'  # Sort key
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'user_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'title',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    table.put_item(Item={'user_id': 'bryan', 'title': 'metal', 'albums': []})
    table.put_item(Item={'user_id': 'bryan', 'title': 'drone', 'albums': []})
    return table
