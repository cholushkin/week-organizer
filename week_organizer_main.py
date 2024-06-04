import argparse
import sys
import os
import csv
import json
import tag_level_suggestion

def load_configuration(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)    

def is_valid_csv_file(file_path):
    try:
        # Attempt to open the file and read the first few lines to validate its structure
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';')
            headers = next(csvreader)
            # Add additional validation logic if needed
            return True
    except Exception as e:
        print(f"Error reading CSV file {file_path}: {e}")
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
    if not data:
        print("No data to display.")
        return
    
    # Print each data row
    for row in data:
        description = row.get('description', '')
        if len(description) > 30:
            description = description[:27] + "..."  # Shorten the description to 30 characters
        row_str = {k: (v if k != 'description' else description) for k, v in row.items()}
        print(row_str)
        
        
def main():
    parser = argparse.ArgumentParser(description="Organizer week plan suggestion utility")

    parser.add_argument(
        '--verbose',
        action='store_true',
        help=''
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='The start date in DD-MMM-YYYY format'
    )
    parser.add_argument(
        '--output',
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
    cfg = load_configuration("task-configuration.json")

    print(f'Start date: {args.start_date}')
    print(f'Output file: {args.output}')
    print(f'Generating a week suggestions...')
    if args.verbose:
        print(f"tasks-dir: {cfg['tasks-dir']}")
    
    tasks_db = load_csv_files_from_directory(cfg["tasks-dir"], args.verbose)
    if args.verbose:
        print_db(tasks_db)

    

if __name__ == "__main__":
    main()
