// Get DOM Elements
const taskDescription = document.getElementById('taskDescription');
const dueTime = document.getElementById('dueTime');
const dueDate = document.getElementById('dueDate');
const addTaskBtn = document.getElementById('addTaskBtn');
const taskList = document.getElementById('taskList');

// Load tasks from localStorage
let tasks = JSON.parse(localStorage.getItem('tasks')) || [];

// Set default date and time values
const now = new Date();
dueDate.value = now.toISOString().split('T')[0];
dueTime.value = now.toTimeString().slice(0, 5);

// Render tasks to the DOM
function renderTasks() {
    taskList.innerHTML = '';
    tasks.forEach((task, index) => {
        const taskElement = document.createElement('div');
        taskElement.className = `task-item ${task.completed ? 'completed' : ''}`;
        
        const dueDateTime = new Date(`${task.dueDate}T${task.dueTime}`);
        const formattedDateTime = dueDateTime.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });

        taskElement.innerHTML = `
            <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''}>
            <div class="task-info">
                <div class="task-description">${task.description}</div>
                <div class="task-due">Due: ${formattedDateTime}</div>
                ${task.completed ? '<div class="task-completed-message">Task completed!</div>' : ''}
            </div>
            <button class="complete-btn" onclick="toggleTask(${index})">Complete</button>
            <button class="delete-btn" onclick="deleteTask(${index})">Delete</button>
        `;

        // Add event listener for checkbox
        const checkbox = taskElement.querySelector('.task-checkbox');
        checkbox.addEventListener('change', () => toggleTask(index));

        taskList.appendChild(taskElement);
    });
    
    // Save current state to localStorage
    localStorage.setItem('tasks', JSON.stringify(tasks));
}

// Create and add a new task
function addTask() {
    const description = taskDescription.value.trim();
    if (description) {
        tasks.push({
            description,
            dueDate: dueDate.value,
            dueTime: dueTime.value,
            completed: false,
            createdAt: new Date().toISOString()
        });
        
        // Reset input fields
        taskDescription.value = '';
        
        // Reset date and time inputs to current time
        const now = new Date();
        dueDate.value = now.toISOString().split('T')[0];
        dueTime.value = now.toTimeString().slice(0, 5);
        
        renderTasks();
    }
}

// Toggle task completion status
function toggleTask(index) {
    tasks[index].completed = !tasks[index].completed;
    renderTasks();
}

// Remove task from the list
function deleteTask(index) {
    tasks.splice(index, 1);
    renderTasks();
}

// Setup Event Listeners
addTaskBtn.addEventListener('click', addTask);
taskDescription.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addTask();
    }
});

// Initialize the application
renderTasks(); 