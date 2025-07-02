# Step 1: This is your Lambda function handler.
# - Receives POST requests from API Gateway
# - Validates input
# - Stores new users in DynamoDB
# - Uses AWS Lambda Powertools for logging

from aws_lambda_powertools import Logger
import boto3
import json
import os
import re
from botocore.exceptions import ClientError

logger = Logger()
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("USERS_TABLE", "users")
table = dynamodb.Table(table_name)

def validate_user_input(data):
    # Step 2: Validate the posted JSON
    errors = []
    if not data.get("username"):
        errors.append("Username is required.")
    if not data.get("email") or not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        errors.append("Valid email is required.")
    if not data.get("password") or len(data["password"]) < 6:
        errors.append("Password must be at least 6 characters.")
    return errors

@logger.inject_lambda_context
def lambda_handler(event, context):
    """
    Step 3: Lambda handler
    - Accepts POST body from API Gateway
    - Validates input
    - Checks for duplicate username
    - Writes to DynamoDB
    """
    try:
        body = event.get("body")
        if body and isinstance(body, str):
            data = json.loads(body)
        elif body and isinstance(body, dict):
            data = body
        else:
            data = event  # for direct Lambda invoke

        logger.info("Received registration request", extra={"data": data})

        errors = validate_user_input(data)
        if errors:
            logger.warning("Validation failed", extra={"errors": errors})
            return {
                "statusCode": 400,
                "body": json.dumps({"success": False, "errors": errors})
            }

        # Step 4: Check for duplicate username in DynamoDB
        existing = table.get_item(
            Key={"username": data["username"]}
        ).get("Item")
        if existing:
            return {
                "statusCode": 409,
                "body": json.dumps({"success": False, "error": "Username already exists."})
            }

        # Step 5: Store new user in DynamoDB
        table.put_item(
            Item={
                "username": data["username"],
                "email": data["email"],
                "password": data["password"]  # In production, hash this!
            }
        )

        logger.info("User registered successfully", extra={"username": data['username']})
        return {
            "statusCode": 201,
            "body": json.dumps({
                "success": True,
                "message": f"User {data['username']} registered successfully."
            })
        }
    except ClientError as ce:
        logger.error("DynamoDB ClientError", extra={"error": str(ce)})
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "error": "Database error"})
        }
    except Exception as e:
        logger.error("Exception in registration", extra={"error": str(e)})
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "error": "Internal server error"})
        }