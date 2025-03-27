from abc import ABC, abstractmethod
import boto3
from datetime import datetime
import uuid
import os

class SubscriberStorage(ABC):
    """Abstract base class for subscriber storage implementations."""
    
    @abstractmethod
    def add_subscriber(self, email):
        """
        Add a new subscriber to the storage.
        
        Args:
            email (str): The subscriber's email address
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_subscribed(self, email):
        """
        Check if an email is already subscribed.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if already subscribed, False otherwise
        """
        pass


class DynamoDBStorage(SubscriberStorage):
    """DynamoDB implementation of subscriber storage."""
    
    def __init__(self, table_name=None, region=None):
        """
        Initialize DynamoDB storage.
        
        Args:
            table_name (str, optional): DynamoDB table name, defaults to env var
            region (str, optional): AWS region, defaults to env var
        """
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE', 'newsletter_subscribers')
        region = region or os.getenv('AWS_REGION', 'us-east-1')
        
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(self.table_name)
    
    def add_subscriber(self, email):
        """Add a subscriber to DynamoDB."""
        try:
            item = {
                'id': str(uuid.uuid4()),
                'email': email.lower().strip(),
                'subscribed_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
                
            self.table.put_item(Item=item)
            return True
        except Exception as e:
            print(f"Error adding subscriber to DynamoDB: {str(e)}")
            return False
    
    def is_subscribed(self, email):
        """Check if email exists in DynamoDB."""
        try:
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email.lower().strip())
            )
            return len(response.get('Items', [])) > 0
        except Exception as e:
            print(f"Error checking subscriber in DynamoDB: {str(e)}")
            return False


class InMemoryStorage(SubscriberStorage):
    """Simple in-memory implementation for testing."""
    
    def __init__(self):
        self.subscribers = {}
    
    def add_subscriber(self, email):
        """Add a subscriber to in-memory storage."""
        email = email.lower().strip()
        self.subscribers[email] = {
            'id': str(uuid.uuid4()),
            'subscribed_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        return True
    
    def is_subscribed(self, email):
        """Check if email exists in memory."""
        return email.lower().strip() in self.subscribers