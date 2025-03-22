import streamlit as st
import json
import os
import boto3
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Configuration
# Get credentials from environment variables
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "us-east-2")  # Changed back to us-east-2
table_name = os.getenv("DYNAMODB_TABLE_NAME", "TodoTable")  # Default table name

# Display configuration info in sidebar
st.sidebar.header("AWS Configuration")
st.sidebar.info(f"AWS Region: {aws_region}")
st.sidebar.info(f"DynamoDB Table: {table_name}")

# Allow overriding config in the UI
with st.sidebar.expander("Override AWS Configuration", expanded=True):
    override_aws_region = st.text_input("AWS Region Override", aws_region)
    override_table_name = st.text_input("Table Name Override", table_name)
    lambda_function_name = st.text_input("Lambda Function Name", "LambdaFunction")
    
    # Use overrides if provided
    if override_aws_region != aws_region:
        aws_region = override_aws_region
    if override_table_name != table_name:
        table_name = override_table_name

# Initialize AWS clients when credentials are available
if aws_access_key and aws_secret_key:
    # Add debug information
    st.sidebar.info(f"Access Key ID: {aws_access_key[:4]}...{aws_access_key[-4:]}")
    st.sidebar.info(f"Using Lambda function: {lambda_function_name}")
    
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )
    
    lambda_client = boto3.client(
        'lambda',
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )
    
    st.sidebar.success("AWS credentials loaded from environment variables!")
else:
    st.sidebar.error("AWS credentials not found in environment variables. Please check your .env file.")
    st.sidebar.info("Make sure your .env file exists and contains AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    dynamodb = None
    lambda_client = None

# Functions to interact with AWS
def load_data():
    if not dynamodb:
        st.warning("AWS credentials not configured. Using sample data.")
        return []
    
    try:
        # Call Lambda function to get all tasks
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({
                "action": "getTodoItems",
                "table_name": table_name,
                "httpMethod": "GET"
            })
        )
        
        # Parse Lambda response
        payload = json.loads(response['Payload'].read().decode())
        
        # Show only essential parts of the response, not the entire response
        st.write("API Status:", payload.get('statusCode', 'Unknown'))
        
        if 'statusCode' in payload and payload['statusCode'] == 200:
            body_content = payload.get('body', '[]')
            if isinstance(body_content, str):
                try:
                    return json.loads(body_content)
                except json.JSONDecodeError as e:
                    st.error(f"JSON parse error: {str(e)}")
                    return []
            return body_content
        else:
            error_message = payload.get('errorMessage', 'Unknown error')
            st.error(f"Error from AWS Lambda: {error_message}")
            return []
    except Exception as e:
        st.error(f"Error loading data from AWS: {str(e)}")
        return []

def save_data(todo):
    if not dynamodb:
        st.warning("AWS credentials not configured. Cannot save data.")
        return False
    
    try:
        # Call Lambda function to add a task
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({
                "action": "addTodoItem",
                "table_name": table_name,
                "httpMethod": "POST",
                "body": json.dumps(todo)
            })
        )
        
        # Parse response from Lambda
        payload = json.loads(response['Payload'].read().decode())
        if 'statusCode' in payload and payload['statusCode'] == 200:
            return True
        else:
            st.error(f"Error from AWS Lambda: {payload}")
            return False
    except Exception as e:
        st.error(f"Error saving data to AWS: {str(e)}")
        return False

def update_task_status(task_id, completed):
    if not dynamodb:
        st.warning("AWS credentials not configured. Cannot update data.")
        return False
    
    try:
        # Call Lambda function to update a task
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({
                "action": "updateTodoItem",
                "table_name": table_name,
                "httpMethod": "PUT",
                "id": task_id,
                "completed": completed
            })
        )
        
        # Parse response from Lambda
        payload = json.loads(response['Payload'].read().decode())
        if 'statusCode' in payload and payload['statusCode'] == 200:
            return True
        else:
            st.error(f"Error from AWS Lambda: {payload}")
            return False
    except Exception as e:
        st.error(f"Error updating data in AWS: {str(e)}")
        return False

def delete_task(task_id):
    if not dynamodb:
        st.warning("AWS credentials not configured. Cannot delete data.")
        return False
    
    try:
        # Call Lambda function to delete a task
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({
                "action": "deleteTodoItem",
                "table_name": table_name,
                "httpMethod": "DELETE",
                "id": task_id
            })
        )
        
        # Parse response from Lambda
        payload = json.loads(response['Payload'].read().decode())
        if 'statusCode' in payload and payload['statusCode'] == 200:
            return True
        else:
            st.error(f"Error from AWS Lambda: {payload}")
            return False
    except Exception as e:
        st.error(f"Error deleting data from AWS: {str(e)}")
        return False

# Main application
st.title('AWS Serverless - To-Do List')

# Add a simple task form
st.header('Add a New Task')
task_input = st.text_input("Task Description")
t_col, d_col = st.columns(2)
with t_col:
    time_input = st.text_input("Due Time (HH:MM)", "08:00")
with d_col:
    date_input = st.text_input("Due Date (YYYY-MM-DD)", datetime.now().strftime("%Y-%m-%d"))

if st.button("Add Task"):
    if task_input:
        if not dynamodb:
            st.error("Please configure AWS credentials first!")
        else:
            # Create a new task
            new_task = {
                "id": str(uuid.uuid4()),
                "description": task_input,
                "due_time": time_input,
                "due_date": date_input,
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            
            # Save to DynamoDB via Lambda
            if save_data(new_task):
                st.success("Task added successfully!")
                st.rerun()
            else:
                st.error("Failed to add task to AWS. Please check logs.")

# Display all tasks
st.header('My Tasks')
todos = load_data()

if not todos:
    st.info("No tasks yet. Add your first task above!")
else:
    # Check if todos is a string (which should be a JSON string)
    if isinstance(todos, str):
        try:
            # If the returned data is a JSON string, try to parse it as an object
            todos = json.loads(todos)
        except json.JSONDecodeError:
            st.error("Invalid data format received from Lambda function")
            todos = []
    
    # Make sure todos is a list
    if not isinstance(todos, list):
        st.error(f"Expected a list of todos, but got {type(todos).__name__}")
        todos = []
    
    # Iterate through each todo item
    for i, todo in enumerate(todos):
        try:
            # If todo is a string, try to parse it
            if isinstance(todo, str):
                try:
                    todo = json.loads(todo)
                except json.JSONDecodeError:
                    st.error(f"Cannot parse todo item {i+1}: {todo}")
                    continue
            
            # Ensure todo is a dictionary
            if not isinstance(todo, dict):
                st.error(f"Todo item {i+1} is not a dictionary: {todo}")
                continue
            
            # Extract task_id safely
            task_id = str(i)
            if isinstance(todo, dict) and 'id' in todo:
                task_id = todo['id']
            
            # Check if the required fields exist
            if 'description' not in todo:
                st.error(f"Todo item {i+1} missing description: {todo}")
                continue
            
            # Get values with safe defaults
            description = todo.get('description', 'No description')
            due_date = todo.get('due_date', 'N/A')
            due_time = todo.get('due_time', 'N/A')
            
            # Display task information
            st.write(f"**Task {i+1}:** {description} (Due: {due_date} {due_time})")
            
            # Task status
            status = "Completed" if todo.get('completed', False) else "Pending"
            st.write(f"**Status:** {status}")
            
            # Complete and Delete buttons
            col1, col2 = st.columns(2)
            with col1:
                if not todo.get('completed', False):
                    if st.button(f"Complete Task {i+1}", key=f"complete_{task_id}"):
                        if update_task_status(task_id, True):
                            st.success(f"Task {i+1} marked as completed!")
                            st.rerun()
                        else:
                            st.error("Failed to update task status.")
            with col2:
                if st.button(f"Delete Task {i+1}", key=f"delete_{task_id}"):
                    if delete_task(task_id):
                        st.success(f"Task {i+1} deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete task.")
            
            # Add a divider between tasks
            st.write("---")
        except Exception as e:
            st.error(f"Error processing todo item {i+1}: {str(e)}")
            continue 