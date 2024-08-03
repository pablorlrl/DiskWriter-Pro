# DiskWriter-Pro

DiskWriter Pro is a tool designed to fill available disk space with binary files. It can be useful for securely wiping data or testing disk capacity. The application features a simple graphical user interface (GUI) for selecting a directory and managing the file creation process.

## Features

- **Simple GUI**: Easily select a directory to fill with files.
- **Progress Feedback**: Visual indicators and messages inform you of the progress and success or failure of the operation.

## Use Cases

- **Determine Drive Capacity**: With this tool you can actually test the real capacity of your drives.
- **Overwrite any past Data**: You can ensure a clean wipe of any disk by emptying it and running this solution to fill it until no space is left.

## Getting Started

### Installation

1. **Download the latest Release**
or
1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd DiskWriter-Pro/src

2. **Generate the executable or run it directly**

- Run "python -m PyInstaller DiskWriter-Pro.spec" from /src to generate yourself an executable
or
- Run the DiskWriter-Pro.py using python

#### Prerequisites (If you want to generate the executable yourself)

- Python 3.12 or higher
- Required Python packages

### Usage

1. **Select the folder to fill up**
2. **Wait until the whole space available is filled up. You will be notified with a popup.**