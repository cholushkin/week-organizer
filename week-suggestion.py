import json
import random
import argparse
import sys

def load_configuration(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["tag-distribution"]["daily-priorities"]

def calculate_tag_ranges(details):
    if len(details["weekly-amount"]) == 1:
        weekly_amount_min = weekly_amount_max = details["weekly-amount"][0]
    else:
        weekly_amount_min, weekly_amount_max = details["weekly-amount"]
    
    daily_amounts = details["daily-amount"]
    if len(daily_amounts) == 1:
        daily_min = daily_max = daily_amounts[0]
    else:
        daily_min, daily_max = daily_amounts
    
    return weekly_amount_min, weekly_amount_max, daily_min, daily_max

def generate_schedule(priorities):
    weekly_schedule = [[] for _ in range(7)]
    tag_counts = {tag: 0 for tag in priorities}
    tag_ranges = {tag: () for tag in priorities}

    for task, details in priorities.items():
        weekly_amount_min, weekly_amount_max, daily_min, daily_max = calculate_tag_ranges(details)
        
        weekly_amount = random.choice(details["weekly-amount"])

        tag_min = weekly_amount_min * daily_min
        tag_max = weekly_amount_max * daily_max
        tag_ranges[task] = (tag_min, tag_max)

        days_to_fill = list(range(7))
        random.shuffle(days_to_fill)
        days_to_fill = days_to_fill[:weekly_amount]

        for day in days_to_fill:
            daily_amount = random.randint(daily_min, daily_max)
            weekly_schedule[day].extend([task] * daily_amount)
            tag_counts[task] += daily_amount

    for day in range(7):
        weekly_schedule[day].sort(
            key=lambda task: priorities[task]["sorting-index"]
        )

    return weekly_schedule, tag_counts, tag_ranges

def adjust_schedule(weekly_schedule, tag_counts, tag_ranges, priorities, easier=True):
    eligible_tags = []
    for tag, (min_count, max_count) in tag_ranges.items():
        if easier and tag_counts[tag] > min_count:
            eligible_tags.append(tag)
        elif not easier and tag_counts[tag] < max_count:
            eligible_tags.append(tag)

    if not eligible_tags:
        print("No tags eligible for adjustment.")
        return weekly_schedule, tag_counts

    tag = random.choice(eligible_tags)
    if easier:
        print(f"Decreasing count of {tag}")
        for day_tasks in weekly_schedule:
            if tag in day_tasks:
                day_tasks.remove(tag)
                tag_counts[tag] -= 1
                break
    else:
        print(f"Increasing count of {tag}")
        # Increase count of the chosen tag by adding it to a random day's tasks
        for day_tasks in weekly_schedule:
            if len(day_tasks) < 7 or tag_counts[tag] < tag_ranges[tag][1]:  # Ensure we're not exceeding max count
                day_tasks.append(tag)
                tag_counts[tag] += 1
                break

    return weekly_schedule, tag_counts


def print_schedule(weekly_schedule, tag_counts, tag_ranges):
    for day, tasks in enumerate(weekly_schedule, start=1):
        print(f"day {day}. {' '.join(tasks)}")

    print("\nTag Counts and Ranges:")
    for tag, count in tag_counts.items():
        min_count, max_count = tag_ranges[tag]
        print(f"{tag}: {count} (min: {min_count}, max: {max_count})")

def main():
    parser = argparse.ArgumentParser(description="Generate a weekly task schedule.")
    parser.add_argument("file", help="Path to the task configuration JSON file")

    args = parser.parse_args()

    try:
        priorities = load_configuration(args.file)
    except FileNotFoundError:
        print(f"Error: The file {args.file} does not exist.")
        sys.exit(1)

    weekly_schedule, tag_counts, tag_ranges = generate_schedule(priorities)
    print_schedule(weekly_schedule, tag_counts, tag_ranges)
    
    # Interactive loop
    while True:
        user_input = input("\nEnter 'inc' to increase, 'dec' to decrease, or 'exit' to exit: ").strip().lower()
        if user_input == "inc":
            weekly_schedule, tag_counts = adjust_schedule(weekly_schedule, tag_counts, tag_ranges, priorities, easier=False)
        elif user_input == "dec":
            weekly_schedule, tag_counts = adjust_schedule(weekly_schedule, tag_counts, tag_ranges, priorities, easier=True)
        elif user_input == "exit":
            break
        else:
            print("Invalid input. Please enter 'inc', 'dec', or 'exit'.")
        
        print_schedule(weekly_schedule, tag_counts, tag_ranges)  # Print updated schedule

if __name__ == "__main__":
    main()
