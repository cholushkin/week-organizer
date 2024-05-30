import json
import random
import argparse
import sys
import os
import platform
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Define a map of hex color codes to ANSI colors
ANSI_COLORS = {
    "#000000": Fore.BLACK,
    "#800000": Fore.RED,
    "#008000": Fore.GREEN,
    "#808000": Fore.YELLOW,
    "#000080": Fore.BLUE,
    "#800080": Fore.MAGENTA,
    "#008080": Fore.CYAN,
    "#c0c0c0": Fore.WHITE,
    "#808080": Fore.LIGHTBLACK_EX,
    "#ff0000": Fore.LIGHTRED_EX,
    "#00ff00": Fore.LIGHTGREEN_EX,
    "#ffff00": Fore.LIGHTYELLOW_EX,
    "#0000ff": Fore.LIGHTBLUE_EX,
    "#ff00ff": Fore.LIGHTMAGENTA_EX,
    "#00ffff": Fore.LIGHTCYAN_EX,
    "#ffffff": Fore.LIGHTWHITE_EX,
    "#ff9900": Fore.YELLOW,       # Add missing colors
    "#9fc5e8": Fore.LIGHTCYAN_EX, # Use closest match for custom colors
    "#9900ff": Fore.LIGHTMAGENTA_EX,
    "#1155cc": Fore.LIGHTBLUE_EX,
    "#6aa84f": Fore.LIGHTGREEN_EX,
    "#bf9000": Fore.YELLOW
}
def clear_console():
    # Check the operating system
    if platform.system() == "Windows":
        os.system("cls")  # For Windows
    else:
        os.system("clear")  # For Unix-like systems

def load_configuration(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data["tag-distribution"]["daily-priorities"]

def get_tag_ranges(details):
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
        weekly_amount_min, weekly_amount_max, daily_min, daily_max = get_tag_ranges(details)
        
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

    # Sort the schedule after adjustment
    for day in range(7):
        weekly_schedule[day].sort(key=lambda task: priorities[task]["sorting-index"])

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
        days_with_tag = [day for day, tasks in enumerate(weekly_schedule) if tag in tasks]
        if days_with_tag:
            day_to_adjust = random.choice(days_with_tag)
            weekly_schedule[day_to_adjust].remove(tag)
            tag_counts[tag] -= 1
    else:
        print(f"Increasing count of {tag}")
        days_without_tag = [day for day, tasks in enumerate(weekly_schedule)]
        if days_without_tag:
            day_to_adjust = random.choice(days_without_tag)
            weekly_schedule[day_to_adjust].append(tag)
            tag_counts[tag] += 1
            
    # Sort the schedule after adjustment
    for day in range(7):
        weekly_schedule[day].sort(key=lambda task: priorities[task]["sorting-index"])

    return weekly_schedule, tag_counts


def print_schedule(weekly_schedule, tag_counts, tag_ranges, priorities):
    def get_color(hex_code):
        return ANSI_COLORS.get(hex_code.lower(), Fore.WHITE)

    for day, tasks in enumerate(weekly_schedule, start=1):
        task_strings = []
        for task in tasks:
            color = get_color(priorities[task]["color"])
            task_strings.append(f"{color}{task}{Style.RESET_ALL}")
        print(f"day {day}. {' '.join(task_strings)}")

    print("\nTag Counts and Ranges:")
    for tag, count in tag_counts.items():
        min_count, max_count = tag_ranges[tag]
        color = get_color(priorities[tag]["color"])
        print(f"{color}{tag}: {count} (min: {min_count}, max: {max_count}){Style.RESET_ALL}")

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
    clear_console()
    print_schedule(weekly_schedule, tag_counts, tag_ranges, priorities)
    
    # Interactive loop
    while True:
        user_input = input(
            """
Enter your option:
  'i' - to increase week difficulty;
  'd' - to decrease week difficulty;
  'r' - to regenerate week;
  'e' - to continue;
"""
        ).strip().lower()
        if user_input == "i":
            weekly_schedule, tag_counts = adjust_schedule(weekly_schedule, tag_counts, tag_ranges, priorities, easier=False)
        elif user_input == "d":
            weekly_schedule, tag_counts = adjust_schedule(weekly_schedule, tag_counts, tag_ranges, priorities, easier=True)
        elif user_input == "r":
            weekly_schedule, tag_counts, tag_ranges = generate_schedule(priorities)
        elif user_input == "e":
            break
        else:
            print("Invalid input. Please enter 'i', 'd', 'r', or 'e'.")
        
        clear_console()  # Clear the console before displaying the updated schedule
        print_schedule(weekly_schedule, tag_counts, tag_ranges, priorities)  # Print updated schedule

if __name__ == "__main__":
    main()
