// todo_manager.js
const fs = require("fs");
const readline = require("readline");

const TODO_FILE = "todo.txt";

function loadTasks() {
    if (fs.existsSync(TODO_FILE)) {
        const data = fs.readFileSync(TODO_FILE, "utf8");
        return data.split("\n").filter(task => task.trim() !== "");
    }
    return [];
}

function saveTasks(tasks) {
    fs.writeFileSync(TODO_FILE, tasks.join("\n"), "utf8");
}

function addTask(tasks) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });
    rl.question("Enter a new task: ", (task) => {
        tasks.push(task);
        saveTasks(tasks);
        console.log(`Task added: ${task}`);
        rl.close();
        main();
    });
}

function viewTasks(tasks) {
    if (tasks.length === 0) {
        console.log("No tasks found.");
    } else {
        console.log("Your tasks:");
        tasks.forEach((task, index) => {
            console.log(`${index + 1}. ${task}`);
        });
    }
}

function deleteTask(tasks) {
    viewTasks(tasks);
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });
    rl.question("Enter the task number to delete: ", (taskNum) => {
        const index = parseInt(taskNum) - 1;
        if (index >= 0 && index < tasks.length) {
            const removedTask = tasks.splice(index, 1);
            saveTasks(tasks);
            console.log(`Task deleted: ${removedTask}`);
        } else {
            console.log("Invalid task number.");
        }
        rl.close();
        main();
    });
}

function main() {
    const tasks = loadTasks();
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });
    console.log("\nTo-Do List Manager");
    console.log("1. View Tasks");
    console.log("2. Add Task");
    console.log("3. Delete Task");
    console.log("4. Exit");
    rl.question("Choose an option: ", (choice) => {
        switch (choice) {
            case "1":
                viewTasks(tasks);
                rl.close();
                main();
                break;
            case "2":
                rl.close();
                addTask(tasks);
                break;
            case "3":
                rl.close();
                deleteTask(tasks);
                break;
            case "4":
                console.log("Goodbye!");
                rl.close();
                process.exit();
                break;
            default:
                console.log("Invalid choice. Please try again.");
                rl.close();
                main();
                break;
        }
    });
}

main();