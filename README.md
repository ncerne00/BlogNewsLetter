
# Newsletter Subscription API

A lightweight, flexible API service for handling newsletter subscriptions with abstract email storage options.

## Overview

This project provides a decoupled newsletter subscription API built with Flask. It's designed to work independently from your main application, allowing for:

- Independent scaling and deployment
- Simplified maintenance
- Greater flexibility in infrastructure choices
- Reusability across multiple frontend projects

The API follows a clean architecture pattern with storage abstraction, making it easy to switch between different database solutions without changing the core business logic.

## Features

- Email validation and sanitization
- Storage abstraction layer (supports multiple storage options: DynamoDB, in-memory storage)
- Configurable via environment variables
- Duplicate subscription detection
- Support for additional subscriber metadata
- Comprehensive error handling and logging

## Planned Features
- More storage options, supporting GCP and Azure

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure environment variables (see Configuration section)

## Configuration

The application can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `STORAGE_TYPE` | Storage implementation to use (`dynamodb` or `memory`) | `dynamodb` |
| `DYNAMODB_TABLE` | DynamoDB table name | `newsletter_subscribers` |
| `AWS_REGION` | AWS region | `us-east-1` |

## API Endpoints

### POST /subscribe-newsletter

Subscribes an email address to the newsletter.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Responses:**

- `201 Created`: Subscription successful
  ```json
  {
    "success": true,
    "message": "Successfully subscribed to the newsletter"
  }
  ```

- `200 OK`: Already subscribed
  ```json
  {
    "success": true,
    "message": "This email is already subscribed"
  }
  ```

- `400 Bad Request`: Validation error
  ```json
  {
    "error": "Invalid email format"
  }
  ```

## Development

### Running Locally

```bash
# Using in-memory storage (for development)
STORAGE_TYPE=memory flask run

# Using DynamoDB (requires AWS credentials)
STORAGE_TYPE=dynamodb flask run
```

### Adding a New Storage Implementation

1. Create a new class that inherits from `SubscriberStorage`
2. Implement the required methods
3. Add the new implementation to the `get_storage()` factory function in `app.py`

Example:
```python
class PostgreSQLStorage(SubscriberStorage):
    def __init__(self, connection_string=None):
        # Initialize connection
        
    def add_subscriber(self, email, metadata=None):
        # Implementation
        
    def is_subscribed(self, email):
        # Implementation
```
## License

MIT