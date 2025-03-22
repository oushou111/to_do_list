# AWS Serverless To-Do Application

A simple to-do list application built with Streamlit and AWS serverless technologies (Lambda + DynamoDB).

## Features

- Add, complete, and delete tasks
- Store tasks in AWS DynamoDB
- Serverless architecture using AWS Lambda
- Environment-based configuration

## Prerequisites

- Python 3.9+
- AWS account with access to Lambda and DynamoDB
- AWS CLI configured (optional, for deployment)

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd to_do
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_aws_access_key_here
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
   AWS_REGION=us-east-2
   DYNAMODB_TABLE_NAME=TodoTable
   ```

4. Create a DynamoDB table named `TodoTable` (or your preferred name) in AWS with:
   - Primary key: `id` (String)

5. Deploy Lambda functions:
   - Create four Lambda functions in AWS: `getTodoItems`, `addTodoItem`, `updateTodoItem`, `deleteTodoItem`
   - For each function, upload the code from `lambda/lambda_function.py`
   - Set the handler to `lambda_function.lambda_handler`
   - Ensure each Lambda function has permission to access your DynamoDB table

## Running the Application

Start the Streamlit application:

```
streamlit run app/streamlit_app.py
```

This will start the application on `http://localhost:8501`.

## Using the Local Version

If you want to test without AWS, you can use the local version:

```
streamlit run app/local_app.py
```

This version stores tasks in a local JSON file instead of AWS DynamoDB.

## Project Structure

- `app/streamlit_app.py` - Main Streamlit application using AWS
- `app/local_app.py` - Local version without AWS dependencies
- `lambda/lambda_function.py` - AWS Lambda function code for all operations
- `.env` - Environment configuration (not in version control)

## Security Notes

- Never commit your `.env` file to version control
- Use IAM roles and policies to restrict Lambda function permissions
- Consider using AWS Secrets Manager for production deployments

## DynamoDB Schema Design

The to-do items table (TodoTable) has the following attributes:

- `id`