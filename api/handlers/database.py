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
    collection.update({'albums': []})
    response = collections.put_item(Item=collection)
    return response


def delete_collection(user_id: str, collection_title):
    response = collections.delete_item(
        Key={
            'user_id': user_id,
            'title': collection_title
            }
        )
    return response


def add_album_to_collection(user_id: str, collection_title: str, album):
    try:
        album_ids_in_collection = [
            x['id'] for x in collections.get_item(
                Key={
                    'user_id': user_id,
                    'title': collection_title}
                )['Item']['albums']
            ]
        album_in_collection = album['id'] in album_ids_in_collection
    except KeyError:
        album_in_collection = False

    if album_in_collection:
        return {'message': 'Album already in collection'}

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


def delete_album_from_collection(user_id: str, collection_title: str, album_id: str):
    collection_albums = collections.get_item(Key={'user_id': user_id, 'title': collection_title})['Item']['albums']
    album_index = [i for i, item in enumerate(collection_albums) if item['id'] == album_id][0]
    
    response = collections.update_item(
        Key={
            'user_id': user_id,
            'title': collection_title
            },
        UpdateExpression=f'REMOVE albums[{album_index}]',
        ReturnValues="UPDATED_NEW"
    )   

    return response

################################

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
