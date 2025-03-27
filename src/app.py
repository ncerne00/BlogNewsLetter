from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import re
import logging
import os
from storage import DynamoDBStorage, InMemoryStorage

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""Initialize storage based on environment variables"""
def get_storage():
    """Factory function to get the appropriate storage implementation."""
    storage_type = os.getenv("STORAGE_TYPE", "dynamodb").lower()
    
    if storage_type == "memory":
        return InMemoryStorage()
    elif storage_type == "dynamodb":
        return DynamoDBStorage()
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")

"""Get storage instance"""
storage = get_storage()

def is_valid_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route("/subscribe-newsletter", methods=["POST"])
def subscribe_newsletter():
    """Check if request contains JSON"""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    """Try to parse JSON data and return generic error message"""
    try:
        json_data = request.get_json()
    except BadRequest:
        return jsonify({"error": "Invalid JSON format"}), 400
    
    """Validate that json_data is a dictionary/object and not something like a list"""
    if not isinstance(json_data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400
    
    """Check if 'email' key exists in JSON"""
    if 'email' not in json_data:
        return jsonify({"error": "Missing required field: email"}), 400
    
    email = json_data.get('email')
    
    """Check if email is a string"""
    if not isinstance(email, str):
        return jsonify({"error": "Email must be a string"}), 400
    
    """Validate email format"""
    if not is_valid_email(email.strip()):
        return jsonify({"error": "Invalid email format"}), 400

    """Process the subscription"""
    try:
        if storage.is_subscribed(email):
            return jsonify({
                "success": True,
                "message": "You are already subscribed to the newsletter"
                }), 200
        
        if storage.add_subscriber(email):
            logger.info(f"Successfully subscribed: {email}")
            return jsonify({
                "success": True,
                "message": "Successfully subscribed to the newsletter"
            }), 201
        else:
            logger.error(f"Failed to add subscriber: {email}")
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        return jsonify({
            "error": "Failed to process subscription"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)