import argparse
import sys
import todos_manager

def process_todos():
    todos_file = 'todos.csv'
    todos = todos_manager.parse_todos(todos_file)
    if not todos:
        print("No valid todos found.")
        return
    
    weekly_suggestions = todos_manager.get_weekly_suggestions(todos)
    
    for idx, suggestion in enumerate(weekly_suggestions, start=1):
        print(f"Day {idx}: {suggestion['title']}")
        print(f"Description: {suggestion['description']}")
        print(f"Priority: {suggestion['priority']}")
        print(f"Prompt: {suggestion['prompt']}\n")

    # Optionally update todos.csv if needed
    update_flag = input("Do you want to update todos.csv by removing the suggested items? (yes/no): ").strip().lower()
    if update_flag == 'yes':
        todos_manager.update_todos_file(todos_file, weekly_suggestions)
        print("todos.csv has been updated.")


def main():
    parser = argparse.ArgumentParser(description="Organizer week plan suggestion utility")

    parser.add_argument(
        '-suggestion',
        action='store_true',
        help='Generate a suggestion for a week'
    )
    parser.add_argument(
        '-start-date',
        type=str,
        required=True,
        help='The start date in DD-MMM-YYYY format'
    )
    parser.add_argument(
        '-output',
        type=str,
        required=True,
        help='The output CSV file name'
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        print("")
        print("Usage example:")
        print("organizer.py -suggestion -start-date 27-May-2024 -output 27-May-2024week.csv")
        sys.exit(1)

    args = parser.parse_args()

    print(f'Start date: {args.start_date}')
    print(f'Output file: {args.output}')
    print(f'Generating a week suggestions...')
    
    process_todos();

if __name__ == "__main__":
    main()
