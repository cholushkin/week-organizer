import csv
import random
import argparse
import sys

def parse_todos(file_path):
    todos = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if 'priority' not in row:
                print(f"Error: 'priority' field missing in row: {row}")
                continue
            try:
                row['priority'] = float(row['priority'])  # Convert priority to float
            except ValueError as e:
                print(f"Error converting priority to float in row: {row}")
                continue
            todos.append(row)
    return todos

def get_weekly_suggestions(todos, num_items=7):
    if len(todos) < num_items:
        print("Warning: Not enough todos to fill the week without duplicates. Some items will be duplicated.")
        todos *= (num_items // len(todos)) + 1

    unique_suggestions = []
    available_todos = todos[:]
    
    while len(unique_suggestions) < num_items:
        selected = random.choices(available_todos, weights=[todo['priority'] for todo in available_todos], k=1)[0]
        unique_suggestions.append(selected)
        available_todos.remove(selected)
        
        if not available_todos:  # Refill available_todos to ensure we can always pick 7 items
            available_todos = todos[:]

    return unique_suggestions

def update_todos_file(file_path, todos_to_remove):
    todos = parse_todos(file_path)
    updated_todos = [todo for todo in todos if todo not in todos_to_remove]
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'description', 'priority', 'prompt']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        
        writer.writeheader()
        writer.writerows(updated_todos)

def main():
    parser = argparse.ArgumentParser(description="Todo manager")
    parser.add_argument('--update-todos', action='store_true', help="Flag to update the todos.csv by removing the suggested items")
    parser.add_argument('--update-todos-used', action='store_true', help="Flag to update the todos-used.csv by adding used items")
    args = parser.parse_args()

    todos_file = 'todos.csv'
    todos_used_file = 'todos-used.csv'
    todos = parse_todos(todos_file)
    if not todos:
        print("No valid todos found.")
        return
    
    weekly_suggestions = get_weekly_suggestions(todos)
    
    for idx, suggestion in enumerate(weekly_suggestions, start=1):
        print(f"Day {idx}: {suggestion['title']}")
        print(f"Description: {suggestion['description']}")
        print(f"Priority: {suggestion['priority']}")
        print(f"Prompt: {suggestion['prompt']}\n")

    if args.update_todos:
        update_todos_file(todos_file, weekly_suggestions)
        print("todos.csv has been updated.")

if __name__ == "__main__":
    main()
