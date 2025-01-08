import json
import boto3
import uuid  # For generating unique IDs

def lambda_handler(event, context):
    try:
        # Parse the request body
        body = json.loads(event['body'])  # Extract 'body' from event
        
        # Extract data from body
        name = body.get("name")
        email = body.get("email")
        attendance = body.get("attendance")
        guests = body.get("guests")
        message = body.get("message")

        # Check required fields
        if not name or not email or not attendance:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }

        # Connect to DynamoDB
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table("RSVPTable")

        # Generate a unique ID for the item
        item_id = str(uuid.uuid4())

        # Save data to DynamoDB
        table.put_item(
            Item={
                "id": item_id,  # Primary key
                "email": email,
                "name": name,
                "attendance": attendance,
                "guests": guests,
                "message": message,
            }
        )

        # Return success response
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "RSVP received!"})
        }
    
    except Exception as e:
        # Log and return error
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
