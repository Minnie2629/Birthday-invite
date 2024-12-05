import json
import boto3
import uuid
from botocore.exceptions import ClientError
from datetime import datetime
import logging

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('RSVPs')  # Your DynamoDB table name

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Log the incoming event for debugging
        logger.info(f"Received event: {json.dumps(event)}")  # Log the incoming event

        # Parse the incoming JSON body
        body = json.loads(event['body'])
        
        # Extract data from the form submission
        name = body.get('name')
        email = body.get('email')
        attendance = body.get('attendance')
        message = body.get('message', 'No message provided')  # Default if no message is provided

        logger.info(f"Parsed data - Name: {name}, Email: {email}, Attendance: {attendance}, Message: {message}")

        # Validation: Ensure that essential fields are present
        if not name or not email or not attendance:
            logger.error("Missing essential fields in the request body")
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing required fields (name, email, or attendance).'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Generate a unique ID for the RSVP entry (optional, if you want to store it as a secondary key or metadata)
        rsvp_id = str(uuid.uuid4())

        # Create a timestamp for when the RSVP was submitted
        timestamp = datetime.utcnow().isoformat()

        # Log data to be inserted into DynamoDB
        logger.info(f"Inserting data into DynamoDB: {name}, {email}, {attendance}, {message}, Timestamp: {timestamp}")

        # Insert data into DynamoDB, using email as the partition key
        response = table.put_item(
            Item={
                'email': email,  # Using email as the partition key
                'name': name,
                'attendance': attendance,
                'message': message,
                'timestamp': timestamp
            },
            ConditionExpression="attribute_not_exists(email)"  # Ensures that the email doesn't already exist
        )

        logger.info(f"Successfully inserted item into DynamoDB. Response: {response}")

        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'RSVP successfully submitted!'}),
            'headers': {'Content-Type': 'application/json'}
        }
    
    except ClientError as e:
        # Log DynamoDB errors and return a failure response
        logger.error(f"DynamoDB ClientError: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error occurred while processing your RSVP. Please try again later.'}),
            'headers': {'Content-Type': 'application/json'}
        }
    
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'An unexpected error occurred. Please try again later.'}),
            'headers': {'Content-Type': 'application/json'}
        }
