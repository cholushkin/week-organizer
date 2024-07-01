import argparse
import sys
import os
import csv
import json
from datetime import datetime
from colorama import Fore, Style, init
import tag_level_suggestion
import task_level_suggestion

def load_configuration(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)


def printError(error_message):
    print(f"{Fore.RED}{error_message}{Style.RESET_ALL}")
available_tags = ['TODO','SKL','HLT','ART','DEV','EDU','LNG','PRJ','ENT']        
def is_valid_csv_file(file_path):
    try:
        # Attempt to open the file and read the first few lines to validate its structure
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';')
            headers = next(csvreader)
            
            # Check for consistent number of columns and empty rows
            for row_number, row in enumerate(csvreader, start=2):
            
                if len(row) != len(headers):
                    printError(f"Error: Inconsistent number of columns at row {row_number}. Expected {len(headers)} but got {len(row)}. (File:{file_path})")
                    return False  
                    
                # check tag value    
                if not row[0] in available_tags:
                    printError(f"Error: {row[0]} tag found which is not allowed literal. (File:{file_path})");
                
                # check task value 
                if not (row[1] and isinstance(row[0], str)):
                    printError(f"Error: '{row[1]}' has wrong value for the task at row {row_number}. (File:{file_path})");
                    
                # check pickup-priority 
                if not (row[3] and row[3].replace('.', '', 1).isdigit() and float(row[3]) >= 0):
                    printError(f"Error: '{row[3]}' has wrong value for pickup-priority at row {row_number}. (File:{file_path})");
                    
                # check days
                if not row[4]:
                    printError(f"Error: '{row[4]}' has wrong value for days at row {row_number}. (File:{file_path})");
                    
                    
            
            # Add additional validation logic if needed
            return True
    except Exception as e:
        printError(f"Error reading CSV file {file_path}: {e}")
        return False
        
def load_csv_files_from_directory(tasks_dir, verbose):
    # Inform about the directory being processed
    if verbose:
        print(f"Loading CSV files from directory: {tasks_dir}")

    all_data = []
    
    # Check if the directory exists
    if not os.path.exists(tasks_dir):
        print(f"Error: Directory {tasks_dir} does not exist.")
        return all_data

    # Iterate over each file in the directory
    for file_name in os.listdir(tasks_dir):
        if file_name.endswith('.csv'):
            file_path = os.path.join(tasks_dir, file_name)
            if verbose:
                print(f"Loading file: {file_path}")
                
            # Check if the CSV file is valid
            if not is_valid_csv_file(file_path):
                continue
            
            # Read the CSV file
            with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile, delimiter=';')
                
                for row in csvreader:
                    row['file'] = file_name                    
                    
                    if not 'tag' in row:
                        print(f"Error: 'tag' key not found in row of file {file_name}: {row}")
                    if not 'task' in row:
                        print(f"Error: 'task' key not found in row of file {file_name}: {row}")
                    if not 'description' in row:
                        print(f"Error: 'description' key not found in row of file {file_name}: {row}")
                    if not 'pickup-priority' in row:
                        print(f"Error: 'pickup-priority' key not found in row of file {file_name}: {row}")
                    if not 'days' in row:
                        print(f"Error: 'days' key not found in row of file {file_name}: {row}")                        
                    if not 'remarks' in row:
                        print(f"Error: 'remarks' key not found in row of file {file_name}: {row}")      
                    if not 'prompt' in row:
                        print(f"Error: 'prompt' key not found in row of file {file_name}: {row}")    
                    
                    all_data.append(row)
    
    if verbose:
        print(f"Total lines loaded: {len(all_data)}")
    return all_data

def print_db(data):
    MAX_VAL_LEN = 24
    if not data:
        print("No data to display.")
        return
    
    # Print each data row
    for row in data:
        # Shorten any value that exceeds MAX_VAL_LEN
        shortened_row = {k: (v if v is None or len(v) <= MAX_VAL_LEN else v[:MAX_VAL_LEN-3] + "...") for k, v in row.items()}
        print(shortened_row)

        
        
def main():
    parser = argparse.ArgumentParser(
        description="Organizer week plan suggestion utility",
        epilog="Usage example:\norganizer.py --cfg task-configuration.json --start-date 27-May-2024 --output 27-May-2024-week-plan.csv"
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Increase output verbosity with detailed logging'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='The start date in DD-MMM-YYYY format. Defaults to today\'s date if not specified.'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='The name of the output CSV file where the week plan will be saved. Defaults to "date-week-plan.csv" if not specified.'
    )
    parser.add_argument(
        '--cfg',
        type=str,        
        help='Path to the task configuration JSON file. Defaults to "task-configuration.json" if not specified'
    )

    args = parser.parse_args()

    # Use current date if --start-date is not specified
    if args.start_date is None:
        args.start_date = datetime.now().strftime("%d-%b-%Y")
    
    # Use default output file name if not specified
    if args.output is None:
        args.output = f"{args.start_date}-week-plan.csv"
        
    # Use default cfg file name if not specified
    if args.cfg is None:
        args.cfg = "task-configuration.json"

    cfg = load_configuration(args.cfg)

    if args.verbose:
        print('Generating a week suggestions...')
        print(f"tasks-dir: {cfg['tasks-dir']}")
        print(f'Start date: {args.start_date}')
        print(f'Output file: {args.output}')
    
    tasks_db = load_csv_files_from_directory(cfg["tasks-dir"], args.verbose)
    #if args.verbose:
    #    print_db(tasks_db)
        
    weekly_schedule, tag_counts, tag_ranges = tag_level_suggestion.run_interactive_mode(False, args.verbose, cfg["tag-distribution"]["daily-priorities"])
    
    task_level_suggestion.run_interactive_mode(args.verbose, weekly_schedule, tag_counts, tag_ranges, tasks_db, args.start_date, cfg["tag-distribution"]["daily-priorities"], args.output)
    
    
    
    

if __name__ == "__main__":
    main()