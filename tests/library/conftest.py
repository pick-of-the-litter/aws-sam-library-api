import json
import os

from boto3 import client
from moto import mock_dynamodb2

from pytest import fixture

ROOT_DIR = os.path.dirname(os.path.abspath("pyproject.toml"))


@fixture
def set_environment():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_REGION"] = "testing"
    os.environ["TABLE_NAME"] = "BooksTable"


@fixture
def library_post_event():
    with open(f"{ROOT_DIR}/events/post_library.json") as data:
        yield json.loads(data.read())


@mock_dynamodb2
def setup_dynamo_db():

    db = client("dynamodb")
    db.create_table(
        TableName="BooksTable",
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
