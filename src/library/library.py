import boto3
import json
import logging
import os
import uuid

from types import SimpleNamespace

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ["TABLE_NAME"]
ERROR_RESPONSE = {
    "headers": {"Content-Type": "application/json"},
    "statusCode": 500,
    "body": json.dumps({"message": "An internal server error occured please contact an administrator."}),
}


def handler(event, context):

    logger.info("Connecting to Dynamo DB.")
    db = boto3.client("dynamodb")
    logger.info("Successfully connected to Dynamo DB.")

    logger.info(f"Handling event:\n{json.dumps(event, indent=2)}")

    if event["httpMethod"] == "POST":
        try:
            logger.info("Creating a new book.")
            return post_book(event, db)
        except Exception as e:
            logger.error(f"The following error occured: {e}")
            return ERROR_RESPONSE

    logger.info("Checking for path parameters.")
    if not event.get("pathParameters"):
        logger.error("Path parameters are missing, request is malformed.")
        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 400,
            "body": "Request is missing the id path parameter",
        }

    if event["httpMethod"] == "GET":
        try:
            logger.info("Getting a book.")
            return get_book(event, db)
        except Exception as e:
            logger.error(f"The following error occured: {repr(e)}")
            return ERROR_RESPONSE
    elif event["httpMethod"] == "PATCH":
        try:
            logger.info("Updating a book.")
            return patch_book(event, db)
        except Exception as e:
            logger.error(f"The following error occured: {repr(e)}")
            return ERROR_RESPONSE
    elif event["httpMethod"] == "DELETE":
        try:
            logger.info("Deleting a book.")
            return delete_book(event, db)
        except Exception as e:
            logger.error(f"The following error occured: {repr(e)}")
            return ERROR_RESPONSE
    else:
        logger.error(f"Incorrect verb used {event['httpMethod']}")
        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 405,
            "body": json.dumps({"message": "Verb not allowed, acceptable verbs are; POST, GET, PATCH and DELETE."}),
        }


def post_book(event, db):
    logger.info("Parsing book data from event body.")
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
    id = event["pathParameters"]["id"]

    logger.info("Parsing book data from event body.")
    response = db.get_item(TableName=TABLE_NAME, Key={"id": {"S": id}})

    if not response.get("Item", False):
        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 400,
            "body": f"Item not found with id: {id}",
        }
    logger.info(f"Book found: {response['Item']}")
    return {
        "headers": {"Content-Type": "application/json"},
        "statusCode": 200,
        "body": json.dumps({"message": f"Found book: {response['Item']}"}),
    }


def patch_book(event, db):
    id = event["pathParameters"]["id"]

    logger.info("Parsing book data from event body.")
    book = json.loads(event["body"], object_hook=lambda d: SimpleNamespace(**d))

    try:
        db.update_item(
            Key={"id": {"S": id}},
            TableName=TABLE_NAME,
            ExpressionAttributeNames={
                "#A": "author",
                "#T": "title",
                "#PC": "pageCount",
            },
            ExpressionAttributeValues={
                ":a": {"S": book.author},
                ":t": {"S": book.title},
                ":pc": {"N": str(book.pageCount)},
            },
            UpdateExpression="SET #A = :a, #T = :t, #PC = :pc",
        )
        logger.info(f"Updated book with id: {id}")
    except db.exceptions.ResourceNotFoundException:
        logger.error(f"Item with id: {id} could not be found.")
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


def delete_book(event, db):
    try:
        id = event["pathParameters"]["id"]
        db.delete_item(
            TableName=TABLE_NAME,
            Key={
                "id": {"S": id},
            },
        )

        logger.info(f"Successfully deleted book with id: {id}")
        return {"statusCode": 204}

    except db.exceptions.ResourceNotFoundException:
        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 400,
            "body": f"Item not found with id: {id}",
        }
