import tkinter as tk
from tkinter import filedialog, messagebox
import os
import psutil
import threading
import webbrowser
from PIL import Image, ImageTk

def get_available_space(directory):
    """Returns the available disk space in bytes using psutil."""
    disk_usage = psutil.disk_usage(directory)
    return disk_usage.free

def create_large_files(directory, file_size_bytes, btn):
    """Creates large files with zeros to fill the entire available space."""
    try:
        large_file_size = 1024 * 1024 * 10  # 10 MB large file size
        num_files = file_size_bytes // large_file_size
        remainder = file_size_bytes % large_file_size
        
        for i in range(num_files):
            file_path = os.path.join(directory, f'filler_{i}.bin')
            with open(file_path, 'wb') as file:
                file.write(b'\x00' * large_file_size)
        
        if remainder > 0: # Adjust the last file to exactly fill the remaining space
            file_path = os.path.join(directory, f'filler_{num_files}.bin')
            with open(file_path, 'wb') as file:
                file.write(b'\x00' * remainder)
        
        messagebox.showinfo("Success", "Successfully filled the available space.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally: # Hide the GIF and re-enable the button after the process is completed
        lbl_gif.pack_forget()
        btn.config(state=tk.NORMAL)

def fill_all_available_space(directory, btn):
    """Fill the entire available space on the selected drive with large files of zeros."""
    try:
        available_space = get_available_space(directory)
        if available_space > 0:
            if messagebox.askyesno("Confirm", f"Are you sure you want to fill the entire available space ({available_space / (1024 * 1024):.2f} MB) with files?"):
                # Disable the button and show the GIF while processing
                btn.config(state=tk.DISABLED)
                lbl_gif.pack(pady=20)
                threading.Thread(target=create_large_files, args=(directory, available_space, btn)).start()
        else:
            messagebox.showwarning("Warning", "No available space found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def select_directory():
    """Prompt user to select a directory and fill all available space."""
    directory = filedialog.askdirectory(title="Select a Directory")
    if directory:
        fill_all_available_space(directory, btn_select_directory)

def on_enter(e):
    """Change button appearance on hover."""
    btn_select_directory.config(bg='#45a049')  # Lighter green

def on_leave(e):
    """Revert button appearance when not hovering."""
    btn_select_directory.config(bg='#4CAF50')  # Original color

def open_donations_page(event):
    """Open the donations page in the web browser."""
    webbrowser.open("https://pabloramos.net/pages/donations.html")

# Set up the Tkinter GUI
root = tk.Tk()
root.title("DiskWriter Pro")
root.geometry("720x480") # Set the initial size of the window

# Determine the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load and set the window icon
icon_path = os.path.join(script_dir, "res/images/favicon.png")
icon = tk.PhotoImage(file=icon_path)
root.iconphoto(True, icon)

root.configure(bg='#222') # Apply dark theme

btn_select_directory = tk.Button( # Create and pack a button to select a directory
    root, 
    text="Select Directory to Fill", 
    font=("Helvetica", 12), 
    command=select_directory, 
    bg='#4CAF50', 
    fg='#fff', 
    activebackground='#2d6b2f', 
    activeforeground='#fff', 
    bd=0, 
    padx=20, 
    pady=10,
    relief='raised',  # Adds a 3D effect
    borderwidth=2, 
    highlightbackground='#2d6b2f',
    highlightcolor='#4CAF50'
)

# Bind hover effects
btn_select_directory.bind("<Enter>", on_enter)
btn_select_directory.bind("<Leave>", on_leave)

btn_select_directory.pack(pady=20)

# Load the GIF and create a label for it
gif_frames = []
gif_path = os.path.join(script_dir, "res/gifs/yo.gif")
gif_image = Image.open(gif_path)
try:
    while True:
        resized_frame = gif_image.copy().resize((200, 200), Image.LANCZOS) # Resize frame
        gif_frames.append(ImageTk.PhotoImage(resized_frame))
        gif_image.seek(len(gif_frames))  # Move to the next frame
except EOFError:
    pass  # End of sequence

gif_index = 0
frame_delay = 10  # Adjust delay to the gif

def update_gif_frame():
    global gif_index
    gif_index = (gif_index + 1) % len(gif_frames)
    lbl_gif.config(image=gif_frames[gif_index])
    lbl_gif.after(frame_delay, update_gif_frame)  # Adjust delay for smoother animation

lbl_gif = tk.Label(root, bg='#222')
update_gif_frame()

lbl_gif.config(width=200, height=200) # Set size for GIF label

lbl_gif.pack_forget() # Initially hide the GIF

lbl_version = tk.Label( # Add version label
    root,
    text="v1.0.0",
    fg="#999",  # Light gray color for version text
    bg="#222",
    font=("Helvetica", 10)
)
lbl_version.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=(10, 5))  # Pady to space it from the donations label

lbl_donations = tk.Label( # Add "Donations" hyperlink label
    root,
    text="Donations",
    fg="#1E90FF",
    bg="#222",
    cursor="hand2",
    font=("Helvetica", 10)
)
lbl_donations.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=(0, 10))

lbl_donations.bind("<Button-1>", open_donations_page) # Bind click event to open the donations page

root.mainloop() # Run the GUI event loop
