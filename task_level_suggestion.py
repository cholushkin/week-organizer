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
        
def get_min_days_from_range_string(ranged_string):
    if '-' in ranged_string:
        min_days, max_days = map(int, t['days'].split('-'))
    else:
        min_days = max_days = int(t['days'])
    return max_days

def generate_suggestion_and_print(tag_counts, weekly_schedule, tasks_db, start_date, priorities):
    start_date = datetime.strptime(start_date, "%d-%b-%Y")
    plan_data = []  # Collect plan data for CSV output

    # todo: some tasks has for example has multiple days, for exmaple 'days=3-5' then such tasks should be distributed among the days (saving the order inside the day)    
    for day_offset, tasks in enumerate(weekly_schedule):
        current_date = start_date + timedelta(days=day_offset)
        day_of_week = current_date.strftime('%A')
        print("")
        print(f"____{current_date.strftime('%d-%b-%Y')} {day_of_week}____")
        
        for task in tasks:
            task = task[1:] # get rid of sharp (#) symbol
                        
            # Filter tasks by the current tag
            filtered_tasks = [t for t in tasks_db if t['tag'] == task]
            if not filtered_tasks:
                print(f"Warning: no available tasks with tag: {task}")
                continue
                
            # todo: filter tasks based on available slots and task "days" (amount of particular tag in the current week and )
            # available in the week task ammount must be >= the minimum days for task            
            #filtered_tasks = [for t in filtered_tasks if get_min_days_from_range_string(t['days']) <= tag_counts
            
            # Calculate weights based on pickup-priority
            weights = [float(t.get('pickup-priority', 0)) for t in filtered_tasks]
            
            # Select a task based on the weights
            selected_task = random.choices(filtered_tasks, weights=weights, k=1)[0]
            
            color = get_color(priorities["#" + selected_task['tag']].get('color', 'white'))
            task_val = sanitize_value(selected_task['task'])
            description_val = sanitize_value(selected_task['description'])
            status_val = "new"
            date_val = current_date.strftime('%d-%b-%Y')
            tags_val = sanitize_value(selected_task['tag'])
            remarks_val = ""
            summary_val = ""
            
            print(f"{color}{tags_val} {task_val} {description_val}{Style.RESET_ALL}")
            
            plan_data.append({
                "Task": task_val,
                "Description": description_val,
                "Status": status_val,
                "Date": date_val,
                "Tags": tags_val,
                "Remarks": remarks_val,
                "Summary": summary_val
            })
            

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
    print(tasks_db)
    plan_data = generate_suggestion_and_print(tag_counts, weekly_schedule, tasks_db, start_date, priorities)
    save_plan_to_csv(plan_data, output_file)
