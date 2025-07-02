# Unit tests for the Lambda function
# - Uses moto to mock DynamoDB
# - Tests validation, registration, and duplicate username

import os
import json
import boto3
from moto import mock_dynamodb
import pytest

# Ensure the USERS_TABLE env var is set for the test
os.environ["USERS_TABLE"] = "users"

from src.app import lambda_handler

@pytest.fixture(autouse=True)
def setup_dynamodb():
    # Sets up a mock DynamoDB table before each test
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        dynamodb.create_table(
            TableName="users",
            KeySchema=[{"AttributeName": "username", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "username", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield

def test_valid_registration():
    event = {
        "body": json.dumps({"username": "alice", "email": "alice@example.com", "password": "password123"})
    }
    context = None
    response = lambda_handler(event, context)
    assert response["statusCode"] == 201
    assert "success" in response["body"]
    assert "alice" in response["body"]

def test_duplicate_username():
    lambda_handler({
        "body": json.dumps({"username": "bob", "email": "bob@example.com", "password": "password123"})
    }, None)
    response = lambda_handler({
        "body": json.dumps({"username": "bob", "email": "bob2@example.com", "password": "password123"})
    }, None)
    assert response["statusCode"] == 409
    assert "Username already exists" in response["body"]

def test_missing_username():
    event = {
        "body": json.dumps({"email": "bob@example.com", "password": "password123"})
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    assert "Username is required" in response["body"]

def test_invalid_email():
    event = {
        "body": json.dumps({"username": "bob", "email": "bobatexample.com", "password": "password123"})
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    assert "Valid email is required" in response["body"]

def test_short_password():
    event = {
        "body": json.dumps({"username": "eve", "email": "eve@example.com", "password": "123"})
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    assert "Password must be at least 6 characters" in response["body"]