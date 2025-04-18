# OpenGD77-CHIRP CSV Converter

This script helps you transform your exported OpenGD77 CSV files into CHIRP format and vice versa.

It supports CSV formats from both OpenGD77 and CHIRP.

---

## Features
- Transform OpenGD77 CSV files into CHIRP format.
- Transform CHIRP CSV files into OpenGD77 format.
- **New:** Support for digital channels (DMR only for now):
  - In the process from OpenGD77 to CHIRP, DMR details are concatenated in the ` comment`  field.
  - For the CHIRP to OpenGD77 process, only the `Chanel Type`  is supported for now.
- **New:** Graphical User Interface (GUI) for a more user-friendly experience:
  - Easily select operations, input files, and output files.
  - Perform transformations with a single click.
  - View notifications for success or errors.

---

## Requirements

- Python 3.6 or higher
- Built-in `csv` module (no additional dependencies required)
- `wxPython` for the GUI (install using `pip install wxPython`)


---

## Installation

1. Clone this repository:
   ```bash
   git clone git@github.com:mrfluxio/opengd77-chrip-csv.git
   ```
2. Navigate to the project directory::
   ```bash
   cd opengd77-chrip-csv
   ```

---
## Usage
Run the script using the following command:
   ```bash
    python opengd77_chirp_csv_coverter.py [operation] [input_file] [output_file] [start_channel]
   ```
---
## Examples

Convert OpenGD77 CSV to CHIRP format:

Use the `gd77` operation with an OpenGD77 CSV file as input.
   ```bash
   python opengd77_chirp_csv_coverter.py gd77 chirp_to_opengd77.csv Channels.csv 1
   ```

Convert CHIRP CSV to OpenGD77 format:
Use the `chirp` operation with a CHIRP CSV file as input.

   ```bash
   python opengd77_chirp_csv_coverter.py chirp Channels.csv chirp_channels.csv 0
   ```
---
## Parameters
- `operation`: The operation to perform. Valid options are `gd77` or `chirp`.
- `input_file`: The path to the input CSV file.
- `output_file`: The path to the output CSV file.
- `start_channel`: The starting channel number for the output file. This is optional and defaults to 0.


---

## Valid Operations

The following operations are supported by the program:

- `gd77`: Transform OpenGD77 CSV files into CHIRP format.
- `chirp`: Transform CHIRP CSV files into OpenGD77 format.

---

## Default File Locations

The program uses the following default file locations for each operation:

- **`gd77`**:
  - Default Input File: `chirp_to_opengd77_channels.csv`
  - Default Output File: `Channels.csv`

- **`chirp`**:
  - Default Input File: `Channels.csv`
  - Default Output File: `exported_channels.csv`

---

## Graphical User Interface (GUI)
You can also use the GUI for a more user-friendly experience.  

1. Run the GUI application:  
    ```bash
    python opengd77_chirp_converter_gui.py
    ```

2. Follow these steps in the GUI:  
- Select the operation from the dropdown menu:
  - Transform CHIRP format to OpenGD77
  - Transform OpenGD77 format to CHIRP
- Browse and select the input file.
- Browse and select the output file.
- Click the Transform button to start the process.
- Notifications will appear to indicate success or errors.

--