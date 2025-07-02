# User Registration Lambda Example (API Gateway + Lambda + DynamoDB)

## Step-by-Step Instructions

### 1. Clone/Download this project and navigate to the folder.

### 2. Create and activate a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies:

```sh
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Run unit tests (DynamoDB is mocked):

```sh
PYTHONPATH=src pytest tests/test_app.py
```

### 5. Build and deploy the stack with AWS SAM:

```sh
sam build
sam deploy --guided
```
- Choose your AWS region and stack name.
- After deployment, note the API Gateway endpoint URL shown in the output.

### 6. Update the integration test with your endpoint:

Edit `tests/test_integration.py` and set the `url` variable to your API Gateway endpoint.

### 7. Run integration tests (optional, after deploy):

```sh
pytest tests/test_integration.py
```

---

## Project Structure

```
sam-app/
├── src/
│   └── app.py
├── tests/
│   ├── test_app.py
│   └── test_integration.py
├── requirements.txt
├── requirements-dev.txt
├── template.yaml
├── .gitignore
└── README.md
```

---

## Notes

- **Password is stored in plaintext** here for simplicity. In production, always hash passwords!
- The username must be unique (enforced by DynamoDB).
- API Gateway exposes a POST endpoint at `/` for registration.
- AWS Lambda Powertools is used for logging.
- The template and tests are ready for you to use and extend!