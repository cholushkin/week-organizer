import csv
import random
from datetime import datetime, timedelta
from tag_level_suggestion import get_color  # Import the get_color function
from colorama import Style

def sanitize_value(value):
    if value is None or value == "":
        return ""
    elif isinstance(value, str):
        return value.strip()
    else:
        print("Error: value isn't a string")
        return value

def generate_suggestion_and_print(tag_counts, weekly_schedule, tasks_db, start_date, priorities):
    start_date = datetime.strptime(start_date, "%d-%b-%Y")
    plan_data = []  # Collect plan data for CSV output

    for day_offset, tasks in enumerate(weekly_schedule):
        current_date = start_date + timedelta(days=day_offset)
        print("")
        print(f"{current_date.strftime('%d-%b-%Y')}")
        
        for task in tasks:
            task = task[1:]
            random.shuffle(tasks_db)  # Shuffle the tasks_db to get random tasks each time
            for task_detail in tasks_db:
                if task_detail['tag'] == task:
                    color = get_color(priorities["#"+task_detail['tag']].get('color', 'white'))
                    print(f"{color}{task_detail['tag']} {task_detail['task']}{Style.RESET_ALL}")
                    
                    task_val = sanitize_value( task_detail['task'] )
                    description_val = sanitize_value( task_detail['description'] )
                    status_val = "new"
                    date_val = current_date.strftime('%d-%b-%Y')
                    tags_val = sanitize_value(task_detail['tag'])
                    remarks_val = ""
                    summary_val = ""
                    
                    #print(f"{task_val}|{description_val}|{status_val}|{date_val}|{tags_val}|{remarks_val}|{summary_val}")
                    #print(f"{task_detail}")
                    
                    plan_data.append({
                        "Task": task_val,
                        "Description": description_val,
                        "Status": status_val,
                        "Date": date_val,
                        "Tags": tags_val,
                        "Remarks": remarks_val,
                        "Summary": summary_val
                    })
                    break  # Move to the next task once a match is found

        # Add an empty row after each day's tasks
        plan_data.append({
            "Task": "",
            "Description": "",
            "Status": "",
            "Date": "",
            "Tags": "",
            "Remarks": "",
            "Summary": ""
        })
    return plan_data

def save_plan_to_csv(plan_data, output_file):
    # Open the CSV file for writing
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Task", "Description", "Status", "Date", "Tags", "Remarks", "Summary"])
        # Write the header
        writer.writeheader()

        for entry in plan_data:            
            writer.writerow(entry)

def run_interactive_mode(verbose, weekly_schedule, tag_counts, tag_ranges, tasks_db, start_date, priorities, output_file):
    plan_data = generate_suggestion_and_print(tag_counts, weekly_schedule, tasks_db, start_date, priorities)
    save_plan_to_csv(plan_data, output_file)
