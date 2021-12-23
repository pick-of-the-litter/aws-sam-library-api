import boto3
import json
import os
import uuid

from types import SimpleNamespace

TABLE_NAME = os.environ["TABLE_NAME"]
ERROR_RESPONSE = {
    "headers": {"Content-Type": "application/json"},
    "statusCode": 500,
    "body": json.dumps({"message": "An internal server error occured please contact an administrator."}),
}


def handler(event, context):

    db = boto3.client("dynamodb")

    if event["httpMethod"] == "POST":
        try:
            return post_book(event, db)
        except Exception:
            return ERROR_RESPONSE

    elif event["httpMethod"] == "GET":
        try:
            return get_book(event, db)
        except Exception:
            return ERROR_RESPONSE

    elif event["httpMethod"] == "PATCH":
        try:
            return patch_book(event, db)
        except Exception:
            return ERROR_RESPONSE
    elif event["httpMethod"] == "DELETE":
        pass
    else:
        pass


def post_book(event, db):
    # contrived example of mapping a dict to an object
    book = json.loads(event["body"], object_hook=lambda d: SimpleNamespace(**d))
    id = str(uuid.uuid4())

    db.put_item(
        TableName=TABLE_NAME,
        Item={
            "id": {"S": id},
            "author": {"S": book.author},
            "title": {"S": book.title},
            "pageCount": {"N": str(book.pageCount)},
        },
    )

    return {
        "headers": {"Content-Type": "application/json"},
        "statusCode": 201,
        "body": json.dumps({"message": f"Created: {book} with id: {id}"}),
    }


def get_book(event, db):
    if not event.get("pathParameters"):
        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 400,
            "body": "Request is missing the id path parameter",
        }

    id = event["pathParameters"]["id"]
    book = db.get_item(TableName=TABLE_NAME, Key={"id": {"S": id}})

    return {
        "headers": {"Content-Type": "application/json"},
        "statusCode": 200,
        "body": json.dumps({"message": f"Found book: {book['Item']}"}),
    }


def patch_book(event, db):
    if not event.get("pathParameters"):
        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 400,
            "body": "Request is missing the id path parameter",
        }

    id = event["pathParameters"]["id"]
    book = json.loads(event["body"], object_hook=lambda d: SimpleNamespace(**d))

    try:
        db.update_item(
            Key={"id": {"S": id}},
            TableName=TABLE_NAME,
            ExpressionAttributeNames={"#A": "author", "#T": "title", "#PC": "pageCount"},
            ExpressionAttributeValues={
                ":a": {"S": book.author},
                ":t": {"S": book.title},
                ":pc": {"N": str(book.pageCount)},
            },
            UpdateExpression="SET #A = :a, #T = :t, #PC = :pc",
        )
    except db.exceptions.ResourceNotFoundException:
        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 400,
            "body": f"Item not found with id: {id}",
        }

    return {
        "headers": {"Content-Type": "application/json"},
        "statusCode": 200,
        "body": json.dumps({"message": f"Updated book with id: {id}"}),
    }
