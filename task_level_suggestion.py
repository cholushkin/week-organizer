import csv
import random
from datetime import datetime, timedelta

def generate_suggestion_and_print(tag_counts, weekly_schedule, tasks_db, start_date):
    start_date = datetime.strptime(start_date, "%d-%b-%Y")
    for day_offset, tasks in enumerate(weekly_schedule):
        current_date = start_date + timedelta(days=day_offset)
        print(f"{current_date.strftime('%d-%b-%Y')}")
        for task in tasks:
            for task_detail in tasks_db:
                if task_detail['tag'] == task:
                    print(f"{task_detail['tag']} {task_detail['task']}")

def run_interactive_mode(verbose, weekly_schedule, tag_counts, tag_ranges, tasks_db, start_date):
    if verbose:
        print("weekly_schedule")
        print(weekly_schedule)
        print("tag_counts")
        print(tag_counts)
        print("tag_ranges")
        print(tag_ranges)

    generate_suggestion_and_print(tag_counts, weekly_schedule, tasks_db, start_date)
