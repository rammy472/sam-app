# Step 7: Integration test (run after deployment)
# - Sends a POST request to the deployed API Gateway endpoint
# - Expects a 201 response for valid registration

import requests
import json

def test_api_gateway_registration():
    # Step 7a: Replace this URL with your deployed API Gateway endpoint after 'sam deploy'
    url = "https://REPLACE_WITH_API_ID.execute-api.YOUR_REGION.amazonaws.com/Prod/"
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "strongpassword"
    }
    resp = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    assert resp.status_code == 201
    assert "success" in resp.text