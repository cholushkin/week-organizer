import csv
import random
from datetime import datetime, timedelta
from tag_level_suggestion import get_color  # Import the get_color function
from colorama import Style
import copy

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


    def get_next_random_task(tasks, tag, max_slots_count):
        filtered_tasks = [t for t in tasks if t['tag'] == tag and get_min_max_days_from_range_string(t['days'])[0]
                          <= max_slots_count]
        if not filtered_tasks:
            print(f"Can't find task {tag} for {max_slots_count} available slots")
            return None, 0
        weights = [float(t.get('pickup-priority', 0)) for t in filtered_tasks]
        # Select a task based on the weights
        selected_task = random.choices(filtered_tasks, weights=weights, k=1)[0]
        tasks.remove(selected_task)
        min_days, max_days = get_min_max_days_from_range_string(selected_task['days'])
        task_days = random.randint(min_days, min(max_days, max_slots_count))
        return selected_task, task_days

    def distribute_tasks(self, tasks_db_origin, tag_counts):
        """
            Algorithm Description:
            1. Make a deep copy of the original tasks database to avoid modifying the original data.
            2. Create a dictionary of available slots by removing the first character from each tag in tag_counts.
            3. For each tag in available slots:
               a. While there are available slots for the tag:
                  i. Get the next random task that fits within the available slots.
                  ii. If no task is found, break the loop.
                  iii. Add the selected task and the number of days it should take to assigned_tasks.
                  iv. Reduce the count of available slots by the number of days assigned to the task.
            4. Distribute the assigned tasks across the week_distribution:
               a. For each assigned task and its days:
                  i. Iterate through each day in the week_distribution.
                  ii. For each slot in the day:
                     - If the slot matches the task's tag and is empty:
                       1. Assign the task to the slot.
                       2. Reduce the number of days remaining for the task.
                       3. Break the loop if all days are assigned.
                  iii. Move to the next day if there are still days remaining for the task.
            5. Print all assigned tasks.
        """
        tasks_db = copy.deepcopy(tasks_db_origin)
        available_slots = {tag[1:]: count for tag, count in tag_counts.items()}

        assigned_tasks = []

        for tag, count in available_slots.items():
            while count > 0:
                selected_task, task_days = get_next_random_task(tasks_db, tag, count)
                if selected_task is None:
                    break
                assigned_tasks.append((selected_task, task_days))
                count -= task_days

        # Distribute assigned tasks to week_distribution
        for assigned_task, task_days in assigned_tasks:
            for day in self.week_distribution:
                for i, tag in enumerate(day["tags"]):
                    if assigned_task['tag'] == tag and task_days > 0 and day["tasks"][i] is None:
                        wtask = {
                            "name": assigned_task["task"],
                            "description": assigned_task["description"],
                            "status": "new",
                            "tag": assigned_task["tag"],
                            "remarks": assigned_task["remarks"] + " " + assigned_task["prompt"],
                            "summary": "",
                        }
                        day["tasks"][i] = wtask
                        task_days -= 1
                        if task_days == 0:
                            break
                if task_days == 0:
                    break



def sanitize_value(value):
    if value is None or value == "":
        return ""
    elif isinstance(value, str):
        return value.strip()
    else:
        print("Error: value isn't a string")
        return value
        
def get_min_max_days_from_range_string(ranged_string):
    if '-' in ranged_string:
        min_days, max_days = map(int, ranged_string.split('-'))
    else:
        min_days = max_days = int(ranged_string)
    return min_days, max_days

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
        week_dist.distribute_tasks(tasks_db, tag_counts)
        distribution = week_dist.get_distribution()
        print_distribution( distribution, weekly_schedule, priorities )        
        
        user_input = input(
            """
Enter your option:
  'r day task' - regenerate specific task; Example: r 1 3
  'r' - to regenerate tasks suggestion for entire week;
  'c' - to continue and create week suggestion csv;c
  'e' - exit
"""
        ).strip().lower()
        if user_input == "r":
            week_dist.distribute_tasks(tasks_db, tag_counts)
        elif user_input == "c":
            print(f"Saving plan to {output_file}")
            save_distribution_to_csv(distribution, output_file)   
            break
        elif user_input == "e":
            print("Abort.")
            return
        else:
            print("Invalid input.")

        
    
    
