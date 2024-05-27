import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Organizer week plan suggestion utility")

    parser.add_argument(
        '-suggestion',
        action='store_true',
        help='Generate a suggestion for a week'
    )
    parser.add_argument(
        '-start-date',
        type=str,
        required=True,
        help='The start date in DD-MMM-YYYY format'
    )
    parser.add_argument(
        '-output',
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

    print(f'Start date: {args.start_date}')
    print(f'Output file: {args.output}')
    print(f'Generating a week suggestions...')

if __name__ == "__main__":
    main()
