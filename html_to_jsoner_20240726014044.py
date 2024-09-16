import html_to_json
import json 
import tkinter as tk
from tkinter import filedialog, messagebox



def select_file_always_on_top():
    # Initialize the Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Ensure the file dialog is always on top
    root.attributes('-topmost', True)

    # Open the file dialog
    file_path = filedialog.askdirectory()

    # Destroy the root window after the file dialog is closed
    root.destroy()

    return file_path


def show_message_box(message):
    # Initialize the Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Show the message box with the provided message
    root.attributes('-topmost', True)

    messagebox.showinfo("Information", message)
    # Destroy the root window after the message box is closed
    root.destroy()

# Example usage
if __name__ == "__main__":
    show_message_box('select html infile.')
    intfile = select_file_always_on_top()
    outfile = intfile.replace('.html', '.json')
    with open(intfile, "r", errors='replace', encoding='utf-8') as f:
        contents = f.read()

    output_json = html_to_json.convert(contents)
    with open(intfile, "w", errors='replace', encoding='utf-8') as f:
        f.write(json.dumps(output_json))
    print(output_json)

    '''
    tell a narrative to contorl it
    but when presented with kuihman handling narrative fine

    '''