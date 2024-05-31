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
    "#ff9900": Fore.YELLOW,
    "#9fc5e8": Fore.LIGHTCYAN_EX,
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

def get_tag_ranges(tag):
    if len(tag["weekly-amount"]) == 1:
        weekly_amount_min = weekly_amount_max = tag["weekly-amount"][0]
    else:
        weekly_amount_min, weekly_amount_max = tag["weekly-amount"]
    
    daily_amounts = tag["daily-amount"]
    if len(daily_amounts) == 1:
        daily_min = daily_max = daily_amounts[0]
    else:
        daily_min, daily_max = daily_amounts
    
    return weekly_amount_min, weekly_amount_max, daily_min, daily_max

def generate_schedule(priorities):
    weekly_schedule = [[] for _ in range(7)]
    tag_counts = {tag: 0 for tag in priorities}
    tag_ranges = {tag: () for tag in priorities}

    for tag_name, tag in priorities.items():
        weekly_amount_min, weekly_amount_max, daily_min, daily_max = get_tag_ranges(tag)
        
        weekly_amount = random.choice(tag["weekly-amount"])

        tag_min = weekly_amount_min * daily_min
        tag_max = weekly_amount_max * daily_max
        tag_ranges[tag_name] = (tag_min, tag_max)

        days_to_fill = list(range(7))
        random.shuffle(days_to_fill)
        days_to_fill = days_to_fill[:weekly_amount]

        for day in days_to_fill:
            daily_amount = random.randint(daily_min, daily_max)
            weekly_schedule[day].extend([tag_name] * daily_amount)
            tag_counts[tag_name] += daily_amount

    # Sort the schedule after adjustment
    for day in range(7):
        weekly_schedule[day].sort(key=lambda tag_name: priorities[tag_name]["sorting-index"])

    return weekly_schedule, tag_counts, tag_ranges

def adjust_schedule(weekly_schedule, tag_counts, tag_ranges, priorities, easier=True):
    eligible_tags = []

    # Identify tags that meet the adjustment criteria
    for tag, (min_count, max_count) in tag_ranges.items():
        if easier:
            if tag_counts[tag] > min_count:
                days_with_tag = [
                    day for day, tags in enumerate(weekly_schedule) 
                    if tags.count(tag) > priorities[tag]["daily-amount"][0]
                ]
                if days_with_tag:
                    eligible_tags.append(tag)
        else:
            if tag_counts[tag] < max_count:
                days_without_tag = [
                    day for day, tags in enumerate(weekly_schedule) 
                    if tags.count(tag) < priorities[tag]["daily-amount"][-1]
                ]
                if days_without_tag:
                    eligible_tags.append(tag)

    if not eligible_tags:
        print("No tags eligible for adjustment.")
        return weekly_schedule, tag_counts

    tag = random.choice(eligible_tags)

    if easier:
        print(f"Decreasing count of {tag}")
        
        days_with_tag = [
            day for day, tags in enumerate(weekly_schedule) 
            if tags.count(tag) > priorities[tag]["daily-amount"][0]
        ]
        
        if not days_with_tag:
            print("No tags eligible for adjustment.")
            return weekly_schedule, tag_counts

        day_to_adjust = random.choice(days_with_tag)
        weekly_schedule[day_to_adjust].remove(tag)
        tag_counts[tag] -= 1
        
    else:
        print(f"Increasing count of {tag}")
        
        days_without_tag = [
            day for day, tags in enumerate(weekly_schedule) 
            if tags.count(tag) < priorities[tag]["daily-amount"][-1]
        ]
        
        if not days_without_tag:
            print("No tags eligible for adjustment.")
            return weekly_schedule, tag_counts

        day_to_adjust = random.choice(days_without_tag)
        weekly_schedule[day_to_adjust].append(tag)
        tag_counts[tag] += 1

    # Sort the schedule after adjustment
    for day in range(7):
        weekly_schedule[day].sort(key=lambda task: priorities[task]["sorting-index"])

    return weekly_schedule, tag_counts


def get_color(hex_code):
    return ANSI_COLORS.get(hex_code.lower(), Fore.WHITE)

def print_schedule(weekly_schedule, tag_counts, tag_ranges, priorities):
    for day, tasks in enumerate(weekly_schedule, start=1):
        task_strings = []
        for task in tasks:
            color = get_color(priorities[task].get("color", "white"))
            task_strings.append(f"{color}{task}{Style.RESET_ALL}")
        print(f"day {day}. {' '.join(task_strings)}")

    print("\nTag Counts and Ranges:")
    for tag, count in tag_counts.items():
        min_count, max_count = tag_ranges[tag]
        color = get_color(priorities[tag].get("color", "white"))
        weekly_amount = priorities[tag]["weekly-amount"]
        daily_amount = priorities[tag]["daily-amount"]
        weekly_range = f"{weekly_amount[0]}" if len(weekly_amount) == 1 else f"{weekly_amount[0]}-{weekly_amount[1]}"
        daily_range = f"{daily_amount[0]}" if len(daily_amount) == 1 else f"{daily_amount[0]}-{daily_amount[1]}"
        print(f"{color}{tag}: {count} (min: {min_count}, max: {max_count}, weekly: {weekly_range}, daily: {daily_range}){Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="Generate a weekly task schedule.")
    parser.add_argument("file", help="Path to the task configuration JSON file")
    parser.add_argument("--clr", action="store_true", help="Clear console before displaying the schedule")

    args = parser.parse_args()

    try:
        priorities = load_configuration(args.file)
    except FileNotFoundError:
        print(f"Error: The file {args.file} does not exist.")
        sys.exit(1)

    weekly_schedule, tag_counts, tag_ranges = generate_schedule(priorities)
    
    if args.clr:
        clear_console()
    print_schedule(weekly_schedule, tag_counts, tag_ranges, priorities)
    
    while True:
        user_input = input(
            """
Enter your option:
  'i' - to increase week difficulty;
  'd' - to decrease week difficulty;
  'r' - to regenerate week;
  'e' - to exit;
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
        
        if args.clr:
            clear_console()
        print_schedule(weekly_schedule, tag_counts, tag_ranges, priorities)

if __name__ == "__main__":
    main()