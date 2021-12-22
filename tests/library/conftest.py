import json
import os
import uuid

from boto3 import client
from moto import mock_dynamodb2

from pytest import fixture

ROOT_DIR = os.path.dirname(os.path.abspath("pyproject.toml"))
TABLE_NAME = "BooksTable"


@fixture
def set_environment():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_REGION"] = "testing"
    os.environ["TABLE_NAME"] = TABLE_NAME


@fixture
def library_post_event():
    with open(f"{ROOT_DIR}/events/post_book.json") as data:
        yield json.loads(data.read())


@fixture
def library_get_event():
    with open(f"{ROOT_DIR}/events/get_book.json") as data:
        yield json.loads(data.read())


@mock_dynamodb2
def setup_dynamo_db():

    db = client("dynamodb")
    db.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    db.put_item(
        TableName=TABLE_NAME,
        Item={
            "id": {"S": str(uuid.uuid4())},
            "author": {"S": "TEST"},
            "title": {"S": "TEST"},
            "pageCount": {"N": str(1)},
        },
    )
