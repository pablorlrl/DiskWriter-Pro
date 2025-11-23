import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import os
import psutil
import threading
import webbrowser
import time
from PIL import Image, ImageTk

stop_event = threading.Event()
max_progress_value = 1

def set_max_progress(val):
    global max_progress_value
    max_progress_value = val

def get_available_space(directory):
    """Returns the available disk space in bytes using psutil."""
    disk_usage = psutil.disk_usage(directory)
    return disk_usage.free

def update_progress(value):
    if max_progress_value > 0:
        width = canvas.winfo_width()
        fill_width = (value / max_progress_value) * width
        canvas.coords(progress_rect, 0, 0, fill_width, 4)
    root.update_idletasks()

def create_large_files(directory, file_size_bytes, btn):
    """Creates large files with zeros to fill the entire available space."""
    try:
        large_file_size = 1024 * 1024 * 1024  # 1 GB large file size
        chunk_size = 1024 * 1024  # 1 MB chunk size
        
        num_files = file_size_bytes // large_file_size
        remainder = file_size_bytes % large_file_size

        # Calculate total chunks for progress bar
        total_chunks = file_size_bytes // chunk_size
        if file_size_bytes % chunk_size > 0:
            total_chunks += 1

        root.after(0, lambda: set_max_progress(total_chunks))
        root.after(0, update_progress, 0)
        
        # Determine the starting index for filenames
        existing_files = [f for f in os.listdir(directory) if f.startswith('filler_') and f.endswith('.bin')]
        max_index = -1
        for f in existing_files:
            try:
                # Extract the number between 'filler_' and '.bin'
                index = int(f.split('_')[1].split('.')[0])
                if index > max_index:
                    max_index = index
            except (ValueError, IndexError):
                pass # Ignore files that don't match the expected format
        
        start_index = max_index + 1
        
        current_chunk = 0
        total_bytes_written = 0
        start_time = time.time()

        for i in range(num_files):
            if stop_event.is_set():
                break
            file_path = os.path.join(directory, f'filler_{start_index + i}.bin')
            with open(file_path, 'wb') as file:
                bytes_written = 0
                while bytes_written < large_file_size:
                    if stop_event.is_set():
                        break
                    write_size = min(chunk_size, large_file_size - bytes_written)
                    file.write(b'\x00' * write_size)
                    bytes_written += write_size
                    total_bytes_written += write_size
                    current_chunk += 1
                    if current_chunk % 10 == 0: # Update UI every 10 chunks
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            speed = (total_bytes_written / (1024 * 1024)) / elapsed_time
                            remaining_bytes = file_size_bytes - total_bytes_written
                            eta = remaining_bytes / (speed * 1024 * 1024)
                            lbl_stats.config(text=f"Speed: {speed:.2f} MB/s | ETA: {eta:.0f} s")
                        root.after(0, update_progress, current_chunk)
        
        if remainder > 0 and not stop_event.is_set(): # Adjust the last file to exactly fill the remaining space
            file_path = os.path.join(directory, f'filler_{start_index + num_files}.bin')
            with open(file_path, 'wb') as file:
                bytes_written = 0
                while bytes_written < remainder:
                    if stop_event.is_set():
                        break
                    write_size = min(chunk_size, remainder - bytes_written)
                    file.write(b'\x00' * write_size)
                    bytes_written += write_size
                    total_bytes_written += write_size
                    current_chunk += 1
                    if current_chunk % 10 == 0:
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            speed = (total_bytes_written / (1024 * 1024)) / elapsed_time
                            remaining_bytes = file_size_bytes - total_bytes_written
                            eta = remaining_bytes / (speed * 1024 * 1024)
                            lbl_stats.config(text=f"Speed: {speed:.2f} MB/s | ETA: {eta:.0f} s")
                        root.after(0, update_progress, current_chunk)
        
        if not stop_event.is_set():
            root.after(0, update_progress, total_chunks)
            messagebox.showinfo("Success", "Successfully filled the available space.")
        else:
            messagebox.showinfo("Stopped", "Operation stopped by user.")
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally: # Hide the GIF and re-enable the button after the process is completed
        root.after(0, reset_ui)

def stop_filling():
    if messagebox.askyesno("Confirm", "Are you sure you want to stop the process?"):
        stop_event.set()

def reset_ui():
    stop_event.clear()
    lbl_gif.pack_forget()
    update_progress(0)
    lbl_stats.config(text="")
    
    # Reset button to original state
    btn_select_directory.config(
        text="Select Directory to Fill", 
        bg='#2ecc71', 
        command=select_directory,
        state=tk.NORMAL
    )
    # Re-bind original hover effects
    btn_select_directory.bind("<Enter>", on_enter)
    btn_select_directory.bind("<Leave>", on_leave)

def fill_all_available_space(directory, btn):
    """Fill the entire available space on the selected drive with large files of zeros."""
    try:
        available_space = get_available_space(directory)
        if available_space > 0:
            if messagebox.askyesno("Confirm", f"Are you sure you want to fill the entire available space ({available_space / (1024 * 1024):.2f} MB) with files?"):
                # Change button to Stop button
                btn.config(
                    text="Stop Filling", 
                    bg='#e74c3c', # Flat Red color
                    command=stop_filling,
                    state=tk.NORMAL
                )
                # Unbind hover effects to keep it red
                btn.unbind("<Enter>")
                btn.unbind("<Leave>")
                
                lbl_gif.pack(pady=20)
                stop_event.clear()
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
    btn_select_directory.config(bg='#27ae60')  # Darker green on hover

def on_leave(e):
    """Revert button appearance when not hovering."""
    btn_select_directory.config(bg='#2ecc71')  # Original flat green

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

root.configure(bg='#2b2b2b') # Apply softer dark theme

# Main Title Label
lbl_title = tk.Label(
    root, 
    text="DiskWriter Pro", 
    font=("Segoe UI", 24, "bold"), 
    fg="#f0f0f0", 
    bg='#2b2b2b'
)
lbl_title.pack(pady=(40, 20))

btn_select_directory = tk.Button( # Create and pack a button to select a directory
    root, 
    text="Select Directory to Fill", 
    font=("Segoe UI", 14, "bold"), 
    command=select_directory, 
    bg='#2ecc71', 
    fg="#ffffff", 
    activebackground='#27ae60', 
    activeforeground='#fff', 
    bd=0, 
    padx=30, 
    pady=15,
    relief='flat',  # Flat design
    cursor="hand2"
)

# Create a canvas for the minimalistic progress bar
bg_color = root.cget("bg")
canvas = tk.Canvas(root, height=4, highlightthickness=0, bg=bg_color)
canvas.pack(side=tk.BOTTOM, fill=tk.X)
progress_rect = canvas.create_rectangle(0, 0, 0, 4, fill="#2ecc71", width=0)

# Stats Label
lbl_stats = tk.Label(
    root, 
    text="", 
    font=("Segoe UI", 10), 
    fg="#f0f0f0", 
    bg='#2b2b2b'
)
lbl_stats.pack(side=tk.BOTTOM, pady=(0, 5))

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
        resized_frame = gif_image.copy().resize((120, 120), Image.LANCZOS) # Resize frame
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

lbl_gif = tk.Label(root, bg='#2b2b2b')
update_gif_frame()

# lbl_gif.config(width=200, height=200) # Removed fixed size to allow auto-sizing

lbl_gif.pack_forget() # Initially hide the GIF

lbl_version = tk.Label( # Add version label
    root,
    text="v1.2.0",
    fg="#999",  # Light gray color for version text
    bg="#2b2b2b",
    cursor="hand2",
    font=("Segoe UI", 10, "bold")
)
lbl_version.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=(0, 5))  # Pady to space it from the donations label
def open_project_page(event):
    webbrowser.open("https://github.com/pablorlrl/DiskWriter-Pro")
def version_on_enter(e):
    lbl_version.config(fg="#FFFFFF")  # when hovered
def version_on_leave(e):
    lbl_version.config(fg="#999")  # back to original
lbl_version.bind("<Enter>", version_on_enter)
lbl_version.bind("<Leave>", version_on_leave)
lbl_version.bind("<Button-1>", open_project_page) # Bind click event to open the project page

lbl_donations = tk.Label( # Add "Donations" hyperlink label
    root,
    text="Donations",
    fg="#3498db",
    bg="#2b2b2b",
    cursor="hand2",
    font=("Segoe UI", 10, "bold")
)
lbl_donations.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=(0, 10))

# Donations label effects
def open_donations_page(event):
    webbrowser.open("https://buy.stripe.com/cN217j4hx1bffN64gg")
def donations_on_enter(e):
    lbl_donations.config(fg="#5dade2")  # when hovered
def donations_on_leave(e):
    lbl_donations.config(fg="#3498db")  # back to original
lbl_donations.bind("<Enter>", donations_on_enter)
lbl_donations.bind("<Leave>", donations_on_leave)
lbl_donations.bind("<Button-1>", open_donations_page) # Bind click event to open the donations page

root.mainloop() # Run the GUI event loop
