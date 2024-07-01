import csv
import random
from datetime import datetime, timedelta
from tag_level_suggestion import get_color  # Import the get_color function
from colorama import Style


# pseudo json representation of week_distribution structure
# week_distribution = [
#  ### Day 1
#  { 
#      "date" : "18-Jun-2024 Tuesday",
#      "tags" : ["HLT", "HLT", "TODO"],
#      "tasks" : [
#          {
#               "name" : "task name",
#               "description" : "task description",
#               "status" : "new",                
#               "tag" : "HLT",
#               "remarks" : "",
#               "summary" : ""
#          },
#          {
#               ... # another task of day 1 HLT
#          },
#          {
#               ... # another task of day 1 TODO
#          },
#      ]
#   },
#   ### Day 2
#   {
#       ...
#   }


class WeekDistribution:
    def __init__(self, weekly_schedule, start_date, verbose):
        self.start_date = datetime.strptime(start_date, "%d-%b-%Y")
        self.verbose = verbose
        self.week_distribution = self._initialize_week_distribution(weekly_schedule)        
        
    def _initialize_week_distribution(self, weekly_schedule):
        week_distribution = []
        for day_offset, tags in enumerate(weekly_schedule):
            current_date = self.start_date + timedelta(days=day_offset)
            day_of_week = current_date.strftime('%A')
            date_string = f"{current_date.strftime('%d-%b-%Y')} {day_of_week}"
            week_distribution.append({
                "date": date_string,
                "tags": [tag[1:] for tag in tags],  # Remove '#' from tags
                "tasks": [None] * len(tags)  # Initialize with empty tasks                
            })
           
        return week_distribution
    
    def get_distribution(self):
        return self.week_distribution

    def distribute_tasks2(self, tasks_db, tag_counts):
        # For each day in the week
        for day in self.week_distribution:
            # For each slot in the day
            for i, tag in enumerate(day["tags"]):

                # Filter tasks by the current tag
                filtered_tasks = [t for t in tasks_db if t['tag'] == tag]
                if not filtered_tasks:
                    print(f"Warning: no available tasks with tag: {tag}")
                    continue

                [print(f"{t.get('pickup-priority', 0)} {t}") for t in filtered_tasks]

                # Calculate weights based on pickup-priority
                weights = [float(t.get('pickup-priority', 0)) for t in filtered_tasks]

                # Select a task based on the weights
                selected_task = random.choices(filtered_tasks, weights=weights, k=1)[0]

                # convert selected_task to week-distribution task format
                wtask = {
                    "name" : selected_task["task"],
                    "description" : selected_task["description"],
                    "status" : "new",
                    "tag" : selected_task["tag"],
                    "remarks" : selected_task["remarks"] + " " + selected_task["prompt"], # todo: real AI responce here
                    "summary" : "",
                }

                # Assign the selected task to the current slot
                day["tasks"][i] = wtask

    def distribute_tasks(self, tasks_db, tag_counts):
        """
        Algorithm:
        1. Initialize available slots based on tag_counts.
        2. While there are available slots:
           a. Iterate over tags with available slots.
           b. For each tag, find tasks that fit in the available slots.
           c. Randomly select a task and determine a random duration within its range.
           d. Distribute the task across available slots, preferring different days.
           e. Update the available slots for the tag.
        3. If no task is found for a tag with available slots, use a generic task.
        """
        available_slots = {tag: count for tag, count in tag_counts.items()}
        task_slots_map = {tag: [] for tag in available_slots}

        # Initialize the task_slots_map with indices of available slots in week_distribution
        for day_index, day in enumerate(self.week_distribution):
            for i, tag in enumerate(day["tags"]):
                if available_slots.get(tag, 0) > 0:
                    task_slots_map[tag].append((day_index, i))

        while any(count > 0 for count in available_slots.values()):
            for tag, count in available_slots.items():
                if count <= 0:
                    continue

                # Filter tasks by the current tag and slots availability
                filtered_tasks = [t for t in tasks_db if
                                  t['tag'] == tag and get_min_days_from_range_string(t['days']) <= count]
                if not filtered_tasks:
                    min_days = min([get_min_days_from_range_string(t['days']) for t in tasks_db if t['tag'] == tag],
                                   default=1)
                    task_days = min(min_days, count)
                    task_slots = task_slots_map[tag][:task_days]
                    for day_index, slot_index in task_slots:
                        self.week_distribution[day_index]["tasks"][slot_index] = replaceNoneTaskWithGeneric(tag,
                                                                                                            min_days)
                    available_slots[tag] -= task_days
                    task_slots_map[tag] = task_slots_map[tag][task_days:]
                    continue

                # Select a task based on the weights and determine random duration
                selected_task = random.choice(filtered_tasks)
                min_days, max_days = map(int, selected_task['days'].split('-')) if '-' in selected_task['days'] else (
                int(selected_task['days']), int(selected_task['days']))
                task_days = random.randint(min_days, min(max_days, count))

                # Distribute the task across available slots, preferring different days
                task_slots = task_slots_map[tag][:task_days]
                for day_index, slot_index in task_slots:
                    wtask = {
                        "name": selected_task["task"],
                        "description": selected_task["description"],
                        "status": "new",
                        "tag": selected_task["tag"],
                        "remarks": selected_task["remarks"] + " " + selected_task["prompt"],
                        "summary": "",
                    }
                    self.week_distribution[day_index]["tasks"][slot_index] = wtask

                available_slots[tag] -= task_days
                task_slots_map[tag] = task_slots_map[tag][task_days:]


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

def print_distribution(distribution, weekly_tag_schedule, priorities):
    for day_index, day in enumerate(distribution):
        print(f"\n{day_index + 1}. {day['date']}")
        for task_index, task in enumerate(day['tasks']):
            if task is None:
                tag = weekly_tag_schedule[day_index][task_index]
                tag = tag[1:]
                task = replaceNoneTaskWithGeneric(task, tag)
            
            tag = '#'+task["tag"]
            color = get_color(priorities[tag].get("color", "white"))
            
            task_name = task["name"]
            task_description = task["description"]
            if len(task_description) > 0:
                print(f"  {task_index + 1}. {color}{tag}:{task_name} = {task_description}{Style.RESET_ALL}")
            else:
                print(f"  {task_index + 1}. {color}{tag}:{task_name}{Style.RESET_ALL}")

def replaceNoneTaskWithGeneric(task, tag):
    if not task is None:
        return task 
    return {
        'name': 'generic-'+tag,
        'description': f"Can't suggest something particular. Please add some new {tag} tasks to backstage", 
        'status': 'new', 
        'tag': tag, 
        'remarks': "Find task by yourself", 
        'summary': ''
    }    
    
    
def save_distribution_to_csv(distribution, output_file):
    # Open the CSV file for writing
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header
        writer.writerow(["Task", "Description", "Status", "Date", "Tags", "Remarks", "Summary"])

        # Write the distribution data
        for day in distribution:
            task_date = day["date"]
            tags = day["tags"]
            tasks = day["tasks"]
            for i, task in enumerate(tasks): 
                if task is None:
                    task_name = "generic-"+tags[i]
                    task_description = f"Can't suggest something particular. Please add some new {tags[i]} tasks to backstage"
                    task_status = "new"
                    task_tag = tags[i]
                    task_remarks = "Find task by yourself"
                    task_summary = ""
                else:
                    task_name = task["name"]
                    task_description = task["description"]
                    task_status = task["status"]
                    task_tag = task["tag"]
                    task_remarks = task["remarks"]
                    task_summary = task["summary"]
               
                writer.writerow([f"{task_name}", f"{task_description}", f"{task_status}", f"{task_date}", f"{task_tag}", f"{task_remarks}", f"{task_summary}"])
            
            # Add an empty row after each day's tasks
            writer.writerow(["", "", "", "", "", "", ""])            
        
        # Write the footer
        writer.writerow(["Task focus", "", "", "", "", "", ""])
        writer.writerow(["Week goal", "", "", "", "", "", ""])
        writer.writerow(["Week summary", "", "", "", "", "", ""])
        

def run_interactive_mode(verbose, weekly_schedule, tag_counts, tag_ranges, tasks_db, start_date, priorities, output_file):
    week_dist = WeekDistribution(weekly_schedule, start_date, verbose)
    
    while True:
        week_dist.distribute_tasks2(tasks_db, tag_counts)
        distribution = week_dist.get_distribution()
        print_distribution( distribution, weekly_schedule, priorities )        
        
        user_input = input(
            """
Enter your option:
  'r day task' - regenerate specific task; Example: r 1 3
  'r' - to regenerate tasks suggestion for entire week;
  'c' - to continue and create week suggestion csv;
  'e' - exit
"""
        ).strip().lower()
        if user_input == "r":
            week_dist.distribute_tasks2(tasks_db, tag_counts)
        elif user_input == "c":
            print(f"Saving plan to {output_file}")
            save_distribution_to_csv(distribution, output_file)   
            break
        elif user_input == "e":
            print("Abort.")
            return
        else:
            print("Invalid input.")

        
    
    
