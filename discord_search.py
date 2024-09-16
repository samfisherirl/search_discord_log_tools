from dotenv import load_dotenv, dotenv_values, set_key
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
from tkcalendar import DateEntry
import sv_ttk
import os
import json
from datetime import datetime
import pytz
import html

def parse_datetime(date_str, time_str):
    """ Helper function to parse date and time strings into a datetime object """
    return datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H-%M").replace(tzinfo=pytz.utc)


def filter_by_datetime(timestamp, date_range=None, time_range=None):
    """ Function to check if a timestamp falls within the specified date and time ranges """
    if date_range:
        date_after = parse_datetime(date_range['after'], '00-00') if 'after' in date_range else None
        date_before = parse_datetime(date_range['before'], '23-59') if 'before' in date_range else None
        if (date_after and timestamp < date_after) or (date_before and timestamp > date_before):
            return False
    if time_range:
        current_time = timestamp.time()
        time_after = datetime.strptime(time_range['after'], "%H-%M").time() if 'after' in time_range else None
        time_before = datetime.strptime(time_range['before'], "%H-%M").time() if 'before' in time_range else None
        if (time_after and current_time < time_after) or (time_before and current_time > time_before):
            return False
    return True


def parse_isoformat_datetime(iso_date):
    if '.' in iso_date:
        iso_date = iso_date.split('.')[0]  # Remove milliseconds if present
    return datetime.fromisoformat(iso_date).replace(tzinfo=pytz.utc)


def find_messages(directory, username, content_filter, date_range=None, time_range=None):
    output_messages = []
    content_filter = content_filter.lower()
    if "," not in content_filter:
        filters = [content_filter]
    else:
        filters = [f.strip() for f in content_filter.split(',')]

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', errors='replace') as file:
                data = json.load(file)
                if "messages" in data:
                    for message in data["messages"]:
                        if "content" in message and "author" in message and message["author"]["name"].lower() == username.lower():
                            message_content_lower = message["content"].lower()
                            if all(f in message_content_lower for f in filters):
                                timestamp_str = message["timestamp"].replace("Z", "")
                                timestamp_utc = parse_isoformat_datetime(timestamp_str)
                                if filter_by_datetime(timestamp_utc, date_range, time_range):
                                    timestamp_est = timestamp_utc.astimezone(pytz.timezone("US/Eastern")).strftime('%Y-%m-%d %H:%M:%S %Z')
                                    output_messages.append({
                                        'timestamp': timestamp_est,
                                        'username': username,
                                        'content': message["content"]
                                    })

    with open('output.html', 'w', encoding='utf-8') as html_file:
        html_file.write('<html><body><h1>Filtered Messages</h1>\n<ul>')
        for msg in output_messages:
            html_file.write(f'<li>{html.escape(msg["timestamp"])} - <b>{html.escape(msg["username"])}</b>: {html.escape(msg["content"])}</li>\n')
        html_file.write('</ul></body></html>')

    # Save to JSON
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(output_messages, json_file, indent=4)

    print("Filtered messages written to output.html and output.json")


class MessageFinderApp:
    def __init__(self, master):
        self.master = master
        master.title("Message Finder")
        sv_ttk.set_theme("dark")

        # Directory frame
        self.directory_frame = ttk.Frame(master)
        self.directory_frame.pack(padx=10, pady=10, fill="x")
        self.directory_label = ttk.Label(self.directory_frame, text="Directory:")
        self.directory_label.pack(side="left")
        self.directory_entry = ttk.Entry(self.directory_frame)
        self.directory_entry.pack(side="left", fill="x", expand=True)
        self.directory_entry.insert(0, os.getcwd())
        self.browse_button = ttk.Button(self.directory_frame, text="Browse", command=self.select_directory)
        self.browse_button.pack(side="right")


        # Frame for both user and content filter
        self.user_content_frame = ttk.Frame(master)
        self.user_content_frame.pack(padx=10, pady=5, fill="x")

        # User filter entries
        self.user_label = ttk.Label(self.user_content_frame, text="User:")
        self.user_label.pack(side="left")
        self.user_entry = ttk.Entry(self.user_content_frame)
        self.user_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Content Filter entries
        self.content_label = ttk.Label(self.user_content_frame, text="Content Filter:")
        self.content_label.pack(side="left")
        self.content_entry = ttk.Entry(self.user_content_frame)
        self.content_entry.pack(side="left", padx=5, fill="x", expand=True)


        # Date and time frame
        self.datetime_frame = ttk.Frame(master)
        self.datetime_frame.pack(padx=10, pady=5, fill="x")

        # Date range entries
        self.date_after_label = ttk.Label(self.datetime_frame, text="Date After:")
        self.date_after_label.pack(side="left")
        self.date_after_entry = DateEntry(self.datetime_frame)
        self.date_after_entry.pack(side="left", padx=5)
        self.date_before_label = ttk.Label(self.datetime_frame, text="Date Before:")
        self.date_before_label.pack(side="left")
        self.date_before_entry = DateEntry(self.datetime_frame)
        self.date_before_entry.pack(side="left", padx=5)

        # Time range entries
        self.time_frame = ttk.Frame(self.datetime_frame)
        self.time_frame.pack(side="left", fill="x", expand=True)

        # Time After
        self.time_after_label = ttk.Label(self.time_frame, text="Time Before (HH:MM):")
        self.time_after_label.pack(side="left")
        self.time_after_entry = ttk.Entry(self.time_frame, width=8)
        self.time_after_entry.pack(side="left", padx=5)

        # Time Before
        self.time_before_label = ttk.Label(self.time_frame, text="Time After (HH:MM):")
        self.time_before_label.pack(side="left")
        self.time_before_entry = ttk.Entry(self.time_frame, width=8)
        self.time_before_entry.pack(side="left", padx=5)

        # Search Button
        self.search_button = ttk.Button(master, text="Search", command=self.handle_search)
        self.search_button.pack(pady=20)

    def select_directory(self):
        directory = filedialog.askdirectory(initialdir=os.getcwd())
        self.directory_entry.delete(0, tk.END)
        self.directory_entry.insert(0, directory)


    def handle_search(self):
        directory = self.directory_entry.get()
        username = self.user_entry.get()
        content_filter = self.content_entry.get()
        after = self.date_after_entry.get_date()
        before = self.date_before_entry.get_date()

        # Formatting dates
        after_formatted = after.strftime("%d-%m-%Y")  # format as "month-date-year"
        before_formatted = before.strftime("%d-%m-%Y")  # format as "month-date-year"

        date_range = {'after': after_formatted, 'before': before_formatted}

        if self.time_after_entry.get().strip() != '' and self.time_before_entry.get().strip() != '':
            time_range = {'after': self.time_after_entry.get().strip(), 'before': self.time_before_entry.get().strip()}
        else:
            time_range = None

        # Assuming 'find_messages' is a function you'll define or import
        result = find_messages(directory, username, content_filter, date_range, time_range)

        # Assuming you print or process the found messages in some way
        print(f"Search in {directory} for user {username} with content filter '{content_filter}', between dates {date_range}, and times {time_range}")
        return result  # Optional depending on what find_messages returns
    
    
    def save_to_env(self, key, value):
        set_key(self.env_file_path, key, value)
        
def main():
    root = tk.Tk()
    app = MessageFinderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
    find_messages(
        os.getcwd(), 
        'spinboy',
        date_range={'after': '01-09-2024', 'before': '05-09-2024'},
        time_range={'after': '02-00', 'before': '05-00'}
    )
