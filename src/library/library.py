import boto3
import json
import os
import uuid


def handler(event, context):

    db = boto3.client("dynamodb")
    table = os.environ["TABLE_NAME"]

    if event["httpMethod"] == "POST":

        data = json.loads(event["body"])
        id = str(uuid.uuid4())

        db.put_item(
            TableName=table,
            Item={
                "id": {"S": id},
                "author": {"S": data["author"]},
                "title": {"S": data["title"]},
                "pageCount": {"N": str(data["pageCount"])},
            },
        )

        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 201,
            "body": json.dumps({"message": f"Created entry for {data['title']} with id: {id}"}),
        }

    elif event["httpMethod"] == "GET":
        pass
    elif event["httpMethod"] == "PUT":
        pass
    elif event["httpMethod"] == "DELETE":
        pass
    else:
        pass
