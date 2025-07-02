import os
import json
import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit

# Initialize Powertools utilities for structured logging, tracing, and metrics
logger = Logger()
tracer = Tracer()
metrics = Metrics(namespace="UserRegistrationService")

# Initialize DynamoDB resource and table object using environment variable
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USERS_TABLE'])

@tracer.capture_lambda_handler  # Adds tracing for AWS X-Ray
@logger.inject_lambda_context   # Injects Lambda context into logs automatically
def lambda_handler(event, context):
    """
    Lambda function for user registration and retrieval.
    Uses AWS Lambda Powertools for Logging, Tracing, and Metrics.
    """

    # Log the incoming event using Powertools Logger
    logger.info({"received_event": event})

    # Get the HTTP method (GET or POST) from the API Gateway event
    method = event.get('httpMethod')

    if method == 'POST':
        # --- Handle user registration (POST) ---
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        email = body.get('email')
        password = body.get('password')

        errors = []
        if not username:
            errors.append("Username is required.")
        if not email or "@" not in email:
            errors.append("Valid email is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")

        if errors:
            # Log warning and add metric for failed registration
            logger.warning({"action": "register", "errors": errors})
            metrics.add_metric(name="FailedRegistrations", unit=MetricUnit.Count, value=1)
            return {
                "statusCode": 400,
                "body": json.dumps({"success": False, "errors": errors})
            }

        # Store user data in DynamoDB (NOTE: Never store raw passwords in production)
        table.put_item(Item={
            "username": username,
            "email": email,
            "password": password
        })

        # Log info and add metric for successful registration
        logger.info({"action": "register", "username": username})
        metrics.add_metric(name="SuccessfulRegistrations", unit=MetricUnit.Count, value=1)
        return {
            "statusCode": 201,
            "body": json.dumps({"success": True, "message": "User registered."})
        }

    elif method == 'GET':
        # --- Handle fetching user by username (GET) ---
        path_params = event.get('pathParameters') or {}
        username = path_params.get('username')
        if not username:
            logger.warning({"action": "fetch_user", "error": "Username path parameter is required"})
            return {
                "statusCode": 400,
                "body": json.dumps({"success": False, "errors": ["Username path parameter is required."]})
            }

        # Fetch user item from DynamoDB
        response = table.get_item(Key={"username": username})

        if "Item" in response:
            item = response["Item"]
            item.pop("password", None)  # Remove password from response
            logger.info({"action": "fetch_user", "username": username})
            metrics.add_metric(name="SuccessfulFetches", unit=MetricUnit.Count, value=1)
            return {
                "statusCode": 200,
                "body": json.dumps({"success": True, "user": item})
            }
        else:
            logger.warning({"action": "fetch_user", "username": username, "error": "User not found"})
            metrics.add_metric(name="FailedFetches", unit=MetricUnit.Count, value=1)
            return {
                "statusCode": 404,
                "body": json.dumps({"success": False, "errors": ["User not found."]})
            }

    else:
        # Log error for unsupported HTTP methods
        logger.error({"action": "unsupported_method", "method": method})
        return {
            "statusCode": 405,
            "body": json.dumps({"success": False, "errors": ["Method not allowed."]})
        }