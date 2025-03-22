import json
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Main handler function for AWS Lambda.
    This function routes to the appropriate handler based on the action parameter.
    """
    # Get action from event or fall back to function name
    action = event.get('action')
    
    # For backward compatibility, if no action is specified, try to use function name
    if not action and context:
        action = context.function_name
    
    # Default to getTodoItems if no action can be determined
    if not action:
        action = "getTodoItems"
    
    # Get table name from event or use default
    table_name = event.get('table_name', 'TodoTable')
    
    # Route to the appropriate handler based on action
    if action == "getTodoItems":
        return get_todo_items(table_name)
    elif action == "addTodoItem":
        return add_todo_item(event, table_name)
    elif action == "updateTodoItem":
        return update_todo_item(event, table_name)
    elif action == "deleteTodoItem":
        return delete_todo_item(event, table_name)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Unknown action: {action}'})
        }

def get_todo_items(table_name):
    """Get all todo items from DynamoDB table"""
    table = dynamodb.Table(table_name)
    
    try:
        # Scan the table to get all items
        response = table.scan()
        items = response.get('Items', [])
        
        # Continue scanning if we have more items (pagination)
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        # Return success response with items
        # Important: ensure proper JSON encoding with no trailing information
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(items, ensure_ascii=False)
        }
    
    except ClientError as e:
        # Return error response
        print(f"Error getting items from DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
    
    except Exception as e:
        # Return error response for other exceptions
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'An unexpected error occurred'
            })
        }

def add_todo_item(event, table_name):
    """Add a new todo item to DynamoDB table"""
    table = dynamodb.Table(table_name)
    
    try:
        # Parse item data from event
        # Check if we have a 'body' parameter (from HTTP API)
        if 'body' in event:
            try:
                # If body is a string, parse it as JSON
                if isinstance(event['body'], str):
                    body_data = json.loads(event['body'])
                else:
                    body_data = event['body']
                    
                # Use the parsed body data
                item = {
                    'id': body_data.get('id'),
                    'description': body_data.get('description', ''),
                    'due_time': body_data.get('due_time', ''),
                    'due_date': body_data.get('due_date', ''),
                    'completed': body_data.get('completed', False),
                    'created_at': body_data.get('created_at', '')
                }
            except Exception as e:
                print(f"Error parsing body: {str(e)}")
                # Fallback to direct event parameters
                item = {
                    'id': event.get('id'),
                    'description': event.get('description', ''),
                    'due_time': event.get('due_time', ''),
                    'due_date': event.get('due_date', ''),
                    'completed': event.get('completed', False),
                    'created_at': event.get('created_at', '')
                }
        else:
            # Direct parameters (no body)
            item = {
                'id': event.get('id'),
                'description': event.get('description', ''),
                'due_time': event.get('due_time', ''),
                'due_date': event.get('due_date', ''),
                'completed': event.get('completed', False),
                'created_at': event.get('created_at', '')
            }
        
        # Put item in DynamoDB
        response = table.put_item(Item=item)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Item added successfully'})
        }
    
    except Exception as e:
        # Return error response
        print(f"Error adding item to DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def update_todo_item(event, table_name):
    """Update a todo item in DynamoDB table"""
    table = dynamodb.Table(table_name)
    
    try:
        # Get item ID and completed status from event
        item_id = event.get('id')
        completed = event.get('completed', False)
        
        # Update item in DynamoDB
        response = table.update_item(
            Key={'id': item_id},
            UpdateExpression="set completed = :c",
            ExpressionAttributeValues={':c': completed},
            ReturnValues="UPDATED_NEW"
        )
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Item updated successfully'})
        }
    
    except Exception as e:
        # Return error response
        print(f"Error updating item in DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def delete_todo_item(event, table_name):
    """Delete a todo item from DynamoDB table"""
    table = dynamodb.Table(table_name)
    
    try:
        # Get item ID from event
        item_id = event.get('id')
        
        # Delete item from DynamoDB
        response = table.delete_item(
            Key={'id': item_id}
        )
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Item deleted successfully'})
        }
    
    except Exception as e:
        # Return error response
        print(f"Error deleting item from DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        } 