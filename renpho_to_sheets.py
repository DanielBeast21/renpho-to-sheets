import os
from renpho import RenphoClient
from datetime import datetime
import pygsheets
from dotenv import load_dotenv

load_dotenv()

# 1. Connect to sheets
client_sheets = pygsheets.authorize(service_file="credentials.json")

sheet_name = os.getenv("GOOGLE_SHEET_NAME")
spreadsheet = client_sheets.open(sheet_name)

worksheet = spreadsheet.worksheet_by_title("Body Comp")

# 2. Fetch latest renpho data
renpho_email = os.getenv("RENPHO_EMAIL")
renpho_password = os.getenv("RENPHO_PASSWORD")

client_renpho = RenphoClient("danielbiancolin@gmail.com", "flashBoy27")
client_renpho.login()

measurements = client_renpho.get_all_measurements()

# Get existing dates to prevent duplicates
existing_dates = worksheet.get_col(1, include_empty=False)

print(f"Found {len(measurements)} total weigh-ins. Analyzing history...")

new_rows_to_add = []

# Loop backwards (oldest to newest) to keep chronological order
for entry in reversed(measurements):
    date_str = entry["localCreatedAt"].split()[0]
    weight = entry["weight"] * 2.20462
    bodyfat = entry.get("bodyfat", 0)
    muscle = entry.get("muscle", 0)
    
    if date_str not in existing_dates and date_str not in [row[0] for row in new_rows_to_add]:
        new_rows_to_add.append([date_str, weight, bodyfat, muscle])
        print(f"Prepared to sync: {date_str}")

# If we found new logs, write them directly to the empty cells
if new_rows_to_add:
    # Find the exact cell coordinate to start writing (e.g., Row 5, Column 1 -> "A5")
    start_row = len(existing_dates) + 1
    start_cell = f"A{start_row}"
    
    # Overwrite the empty grid space in one single call without shifting cells
    worksheet.update_values(crange=start_cell, values=new_rows_to_add)
    print(f"🎉 Success! Wrote {len(new_rows_to_add)} new entries starting at cell {start_cell}!")
else:
    print("😎 Your sheet is already completely up to date.")