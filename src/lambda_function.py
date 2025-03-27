import json
import re
import logging
import os
from storage import DynamoDBStorage, InMemoryStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_storage():
    """Factory function to get the appropriate storage implementation."""
    storage_type = os.getenv("STORAGE_TYPE", "dynamodb").lower()
    if storage_type == "memory":
        return InMemoryStorage()
    elif storage_type == "dynamodb":
        return DynamoDBStorage()
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")

storage = get_storage()

def is_valid_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def lambda_handler(event, context):
    """
    AWS Lambda handler function for newsletter subscription.
    
    Parameters:
    - event: The event dict that contains the request data
    - context: The context object for the Lambda function
    
    Returns:
    - dict with statusCode, headers, and body
    """
    try:
        """Handling API Gateway"""
        if 'body' in event:
            if event['body'] is None:
                return format_response({"error": "Request body is required"}, 400)
            
            if isinstance(event['body'], str):
                try:
                    json_data = json.loads(event['body'])
                except json.JSONDecodeError:
                    return format_response({"error": "Invalid JSON format"}, 400)
            else:
                json_data = event['body']
        else:
            """Direct Lambda invocation"""
            json_data = event
            
        """Validate that json_data is a dictionary/object"""
        if not isinstance(json_data, dict):
            return format_response({"error": "Request body must be a JSON object"}, 400)
            
        """Check if 'email' key exists in JSON"""
        if 'email' not in json_data:
            return format_response({"error": "Missing required field: email"}, 400)
            
        email = json_data.get('email')
        
        """Check if email is a string"""
        if not isinstance(email, str):
            return format_response({"error": "Email must be a string"}, 400)
            
        """Validate email format"""
        if not is_valid_email(email.strip()):
            return format_response({"error": "Invalid email format"}, 400)
            
        """Process the subscription"""
        try:
            if storage.is_subscribed(email):
                return format_response({
                    "success": True,
                    "message": "You are already subscribed to the newsletter"
                }, 200)
                
            if storage.add_subscriber(email):
                logger.info(f"Successfully subscribed: {email}")
                return format_response({
                    "success": True,
                    "message": "Successfully subscribed to the newsletter"
                }, 201)
            else:
                logger.error(f"Failed to add subscriber: {email}")
                return format_response({
                    "error": "Failed to process subscription"
                }, 500)
                
        except Exception as e:
            logger.error(f"Subscription error: {str(e)}")
            return format_response({
                "error": "Failed to process subscription"
            }, 500)
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return format_response({
            "error": "Internal server error"
        }, 500)

def format_response(body, status_code):
    """Helper function to format the API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }