import streamlit as st
import json
import os
import uuid
from datetime import datetime

# File to store data
DATA_FILE = "todos.json"

# Functions to interact with local storage
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return []

def save_data(todos):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(todos, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

# Main application
st.title('To-Do List App (Local Version)')
st.caption("Using local JSON storage instead of AWS")

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
        # Load existing tasks
        todos = load_data()
        
        # Create a new task
        new_task = {
            "id": str(uuid.uuid4()),
            "description": task_input,
            "due_time": time_input,
            "due_date": date_input,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        
        # Add new task and save
        todos.append(new_task)
        if save_data(todos):
            st.success("Task added successfully!")
            st.rerun()
        else:
            st.error("Failed to add task. Please check logs.")

# Display all tasks
st.header('My Tasks')
todos = load_data()

if not todos:
    st.info("No tasks yet. Add your first task above!")
else:
    for i, todo in enumerate(todos):
        # Display each task in a simple format
        st.write(f"**Task {i+1}:** {todo['description']} (Due: {todo['due_date']} {todo['due_time']})")
        
        # Task status
        status = "Completed" if todo.get('completed') else "Pending"
        st.write(f"**Status:** {status}")
        
        # Complete and Delete buttons
        col1, col2 = st.columns(2)
        with col1:
            if not todo.get('completed'):
                if st.button(f"Complete Task {i+1}", key=f"complete_{todo['id']}"):
                    todo['completed'] = True
                    if save_data(todos):
                        st.success(f"Task {i+1} marked as completed!")
                        st.rerun()
                    else:
                        st.error("Failed to update task status.")
        with col2:
            if st.button(f"Delete Task {i+1}", key=f"delete_{todo['id']}"):
                todos.remove(todo)
                if save_data(todos):
                    st.success(f"Task {i+1} deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete task.")
        
        # Add a divider between tasks
        st.write("---") 