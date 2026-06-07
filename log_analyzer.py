#!/usr/bin/env python
import argparse
import csv
import json
from parse_timestamp import parse_timestamp


from_timestamp = None
to_timestamp = None
parser = argparse.ArgumentParser(description="Log analyzer")
parser.add_argument("-f", type=str, required=True,help="Path to the log file")
parser.add_argument("--from", type=str,help="Starting date")
parser.add_argument("--to", type=str,help="Ending Date")
parser.add_argument("-export", type=str, help="Export summary to CSV")


args = parser.parse_args()
from_timestamp = parse_timestamp(getattr(args, "from"))
to_timestamp = parse_timestamp(getattr(args, "to"))
errors = warnings = info = 0
error_dict = {}
most_common_error = ""
error_timestamps = []
most_common_error_count = 0
plain_text_errors = 0
with open(args.f, "r") as file:
    lines = file.readlines()
for i, line in enumerate(lines, start=1):
    line = line.strip()
    try:
        data = json.loads(line)
        if isinstance(data, dict):
            level = data.get("level")
            error = data.get('error')
            timestamp = data.get('timestamp')
            match level:
                case "ERROR":
                    parsed_timestamp = parse_timestamp(timestamp)
                    if from_timestamp and (parsed_timestamp is None or parsed_timestamp < from_timestamp):
                        continue
                    if to_timestamp and (parsed_timestamp is None or parsed_timestamp > to_timestamp):
                        continue
                    errors += 1
                    if error in error_dict:
                        error_dict[error] += 1
                    else:
                        error_dict[error] = 1
                    error_timestamps.append(timestamp)
                case "WARNING":
                    warnings += 1
                case "INFO":
                    info += 1
            print(f"Line {i}: JSON log")
            print(data)
        else:
            print(f"Line {i}: Valid JSON but not an object")

    except json.JSONDecodeError:
        plain_text_errors += 1
        print(f"Line {i}: Plain text log")
        print(line)
print(f"Summary: {errors} errors, {warnings} warnings, {info} info messages")
for key in error_dict:
    if error_dict[key] > most_common_error_count:
        most_common_error = key
        most_common_error_count = error_dict[key]
print(f"Total Logs: {plain_text_errors + warnings + info + errors}")
print(f"Errors: {errors}")
print(f"Warnings: {warnings}")
print(f"Info: {info}")
print(f"Most frequest error: {most_common_error}")
print(f"Error timestamps: {error_timestamps}")

if args.export:
    with open(args.export, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["metric", "value"])
        writer.writerow(["total_logs", plain_text_errors + warnings + info + errors])
        writer.writerow(["errors", errors])
        writer.writerow(["warnings", warnings])
        writer.writerow(["info", info])
        writer.writerow(["most_common_error", most_common_error])
