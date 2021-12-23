import boto3
import json
import os
import uuid

from types import SimpleNamespace


def handler(event, context):

    db = boto3.client("dynamodb")
    table = os.environ["TABLE_NAME"]

    if event["httpMethod"] == "POST":
        # contrived example of mapping a dict to an object
        book = json.loads(event["body"], object_hook=lambda d: SimpleNamespace(**d))
        id = str(uuid.uuid4())

        db.put_item(
            TableName=table,
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

    elif event["httpMethod"] == "GET":
        if not event.get("pathParameters"):
            return {
                "headers": {"Content-Type": "application/json"},
                "statusCode": 400,
                "body": "Request is missing the id path parameter",
            }

        id = event["pathParameters"]["id"]
        book = db.get_item(TableName=table, Key={"id": {"S": id}})

        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 200,
            "body": json.dumps({"message": f"Found book: {book['Item']}"}),
        }

    elif event["httpMethod"] == "PATCH":
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
                TableName=table,
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
    elif event["httpMethod"] == "DELETE":
        pass
    else:
        pass
