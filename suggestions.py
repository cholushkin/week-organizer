import json
import random

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_task_amount(task):
    if isinstance(task['daily-amount'], str):
        min_amount, max_amount = map(int, task['daily-amount'].split('-'))
        return random.randint(min_amount, max_amount)
    return task['daily-amount']

def generate_daily_schedule(tasks):
    daily_schedule = []
    for task_id, task in sorted(tasks.items(), key=lambda x: x[1]['sorting-index']):
        if random.random() <= task['daily-prob']:
            amount = get_task_amount(task)
            daily_schedule.extend([task_id] * amount)
    return daily_schedule

def generate_weekly_schedule(tasks, days=7):
    weekly_schedule = []
    for day in range(days):
        daily_schedule = generate_daily_schedule(tasks)
        weekly_schedule.append(f"day {day + 1}. " + " ".join(daily_schedule))
    return weekly_schedule

def main():
    file_path = 'suggestions.json'
    data = read_json(file_path)
    tasks = data['suggestion']['daily-priorities']
    weekly_schedule = generate_weekly_schedule(tasks)
    
    for day_schedule in weekly_schedule:
        print(day_schedule)

if __name__ == "__main__":
    main()
