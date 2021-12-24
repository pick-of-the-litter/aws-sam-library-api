import json
import os

from boto3 import client
from moto import mock_dynamodb2

from pytest import fixture

ROOT_DIR = os.path.dirname(os.path.abspath("pyproject.toml"))
os.environ["TABLE_NAME"] = "BookTable"


@fixture
def set_environment():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_REGION"] = "testing"


@fixture
def library_post_event():
    with open(f"{ROOT_DIR}/events/post_book.json") as data:
        yield json.loads(data.read())


@fixture
def library_get_no_parameters_event():
    with open(f"{ROOT_DIR}/events/get_book_no_parameters.json") as data:
        yield json.loads(data.read())


@fixture
def library_get_event():
    with open(f"{ROOT_DIR}/events/get_book.json") as data:
        yield json.loads(data.read())


@fixture
def library_patch_event():
    with open(f"{ROOT_DIR}/events/patch_book.json") as data:
        yield json.loads(data.read())


@fixture
def library_delete_event():
    with open(f"{ROOT_DIR}/events/delete_book.json") as data:
        yield json.loads(data.read())


@mock_dynamodb2
def setup_dynamo_db():

    db = client("dynamodb")
    db.create_table(
        TableName=os.environ["TABLE_NAME"],
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    db.put_item(
        TableName=os.environ["TABLE_NAME"],
        Item={
            "id": {"S": "123"},
            "author": {"S": "TEST"},
            "title": {"S": "TEST"},
            "pageCount": {"N": str(1)},
        },
    )
