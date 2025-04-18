import csv
import logging
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Constants
DEFAULT_GD_INPUT_FILE = 'chirp_to_opengd77_channels.csv'
DEFAULT_GD_OUTPUT_FILE = 'Channels.csv'
DEFAULT_CHIRP_INPUT_FILE = 'Channels.csv'
DEFAULT_CHIRP_OUTPUT_FILE = 'exported_channels.csv'
DEFAULT_START_CHANNEL = 0
# Default operation mode
DEFAULT_OPERATION = "gd77"

# Define a dictionary for valid operations with default input and output files
VALID_OPERATIONS = {
    "gd77": {
        "description": "Transform OpenGD77 CSV files",
        "default_input_file": DEFAULT_GD_INPUT_FILE,
        "default_output_file": DEFAULT_GD_OUTPUT_FILE,
    },
    "chirp": {
        "description": "Transform CHIRP CSV files",
        "default_input_file": DEFAULT_CHIRP_INPUT_FILE,
        "default_output_file": DEFAULT_CHIRP_OUTPUT_FILE,
    },
}

# Constants for repeated literals
TX_FREQUENCY = "Tx Frequency"
RX_FREQUENCY = "Rx Frequency"
CHANNEL_NAME = "Channel Name"
POWER = "Power"
ALL_SKIP = "All Skip"
RX_TONE = "RX Tone"
TX_TONE = "TX Tone"
LOCATION = "Location"
NAME = "Name"
FREQUENCY = "Frequency"
DUPLEX = "Duplex"
OFFSET = "Offset"
TONE = "Tone"
RTONE_FREQ = "rToneFreq"
CTONE_FREQ = "cToneFreq"
DTCS_CODE = "DtcsCode"
DTCS_POLARITY = "DtcsPolarity"
RX_DTCS_CODE = "RxDtcsCode"
CROSS_MODE = "CrossMode"
MODE = "Mode"
SKIP = "Skip"
COMMENT = "Comment"
CHANNEL_TYPE = "Channel Type"
BANDWIDTH_KHZ = "Bandwidth (kHz)"
TONE_TONE = "Tone->Tone"


# Default values for fields not in the input format
CD_DEFAULT_VALUES = {
    CHANNEL_TYPE: "Analogue",
    BANDWIDTH_KHZ: "25",
    "Colour Code": "",
    "Timeslot": "",
    "Contact": "",
    "TG List": "",
    "DMR ID": "",
    "TS1_TA_Tx": "",
    "TS2_TA_Tx ID": "",
    "RX Tone": "None",
    "TX Tone": "None",
    "Squelch": "Disabled",
    "Power": "Master",
    "Rx Only": "No",
    "Zone Skip": "No",
    "All Skip": "No",
    "TOT": "0",
    "VOX": "Off",
    "No Beep": "No",
    "No Eco": "No",
    "APRS": "None",
    "Latitude": "0.128",
    "Longitude": "0.008",
    "Use Location": "No"
}

CHIRP_DEFAULT_VALUES = {
    "TStep": "12.500",
    "Power": "50W",
    "Comment": "",
    "URCALL": "",
    "RPT1CALL": "",
    "RPT2CALL": "",
    "DVCODE": ""
}

GD77_FIELDNAMES = [
    "Channel Number", CHANNEL_NAME, CHANNEL_TYPE, RX_FREQUENCY, TX_FREQUENCY,
    BANDWIDTH_KHZ, "Colour Code", "Timeslot", "Contact", "TG List", "DMR ID",
    "TS1_TA_Tx", "TS2_TA_Tx ID", RX_TONE, TX_TONE, "Squelch", POWER, "Rx Only",
    "Zone Skip", ALL_SKIP, "TOT", "VOX", "No Beep", "No Eco", "APRS", "Latitude",
    "Longitude", "Use Location"
]

CHIRP_FIELDNAMES = [
    "Location", "Name", "Frequency", "Duplex", "Offset", "Tone", "rToneFreq",
    "cToneFreq", "DtcsCode", "DtcsPolarity", "RxDtcsCode", "CrossMode", "Mode",
    "TStep", "Skip", "Power", "Comment", "URCALL", "RPT1CALL", "RPT2CALL",
    "DVCODE"
]


# Helper functions
def calculate_tx_frequency(row):
    """Calculate Tx Frequency based on Duplex and Offset."""
    if row["Duplex"] == "" or row["Offset"] == "" or abs(float(row["Offset"]) - 0.0) < 1e-9:
        return row["Frequency"]
    offset = float(row["Offset"])
    frequency = float(row["Frequency"])
    return str(frequency + offset if row["Duplex"] == "+" else frequency - offset)


def calculate_power(row):
    """Determine Power level based on the value in row['Power']."""
    power = float(row["Power"].rstrip("W"))
    if power < 1.0:
        return "P1"
    elif 1.0 <= power < 2.0:
        return "P5"
    elif 2.0 <= power < 3.0:
        return "P6"
    elif 3.0 <= power < 4.0:
        return "P7"
    elif 4.0 <= power < 5.0:
        return "P8"
    elif row["Power"].rstrip("W") == "5.0":
        return "P9"
    return CD_DEFAULT_VALUES["Power"]


def extract_polarity(value):
    """Extract polarity 'R' if 'II' is present, 'N' if 'NN' is present."""
    if "RR" in value:
        return "I"
    elif "NN" in value:
        return "N"
    return ""


def calculate_tone(row: Dict[str, Any], tone_type: str) -> str:
    """Calculate RX or TX Tone based on the Tone type."""
    if row["Tone"] == "DTCS":
        return f"D{row['DtcsCode']}{extract_polarity(row['DtcsPolarity'])}"
    elif row["Tone"] == "Tone":
        return row[f"{tone_type}ToneFreq"]
    elif row["Tone"] == "TSQL":
        return "None"
    elif row["Tone"] == "Cross":
        if row["CrossMode"] == TONE_TONE:
            return row[f"{tone_type}ToneFreq"]
        elif tone_type == "r":
            return f"D{row['RxDtcsCode']}{extract_polarity(row['DtcsPolarity'])}"
        elif tone_type == "c":
            return f"D{row['DtcsCode']}{extract_polarity(row['DtcsPolarity'])}"
    return "None"


def transform_row(row: Dict[str, Any], channel_number: int) -> Dict[str, Any]:
    """Transform a single row into the target format."""
    try:
        return {
            **CD_DEFAULT_VALUES,
            "Channel Number": channel_number,
            CHANNEL_NAME: row["Name"],
            BANDWIDTH_KHZ: 12.5 if row["Mode"] == "NFM" else 25,
            RX_FREQUENCY: f"{float(row['Frequency']):.5f}",
            TX_FREQUENCY: f"{float(calculate_tx_frequency(row)):.5f}",
            RX_TONE: calculate_tone(row, "r"),
            TX_TONE: calculate_tone(row, "c"),
            POWER: calculate_power(row),
            ALL_SKIP: "Yes" if row["Skip"] == "S" else CD_DEFAULT_VALUES[ALL_SKIP]
        }
    except KeyError as e:
        logging.error(f"Missing key {e} in row: {row}")
        raise
    except ValueError as e:
        logging.error(f"Invalid value in row: {row}")
        raise


def determine_duplex(tx_frequency, rx_frequency):
    """Determine the Duplex value."""
    tx = float(tx_frequency)
    rx = float(rx_frequency)
    if tx > rx:
        return "+"
    elif tx == rx:
        return ""
    return "-"


def calculate_offset(tx_frequency, rx_frequency):
    """Calculate the Offset value."""
    tx = float(tx_frequency)
    rx = float(rx_frequency)
    if tx != rx:
        return abs(int(tx * 1000) - int(rx * 1000)) / 1000
    return ""


def determine_tone(rx_tone, tx_tone):
    """Determine the Tone value."""
    if rx_tone != "None" and tx_tone != "None" and rx_tone != tx_tone:
        return "Cross"
    if rx_tone.startswith("D") or tx_tone.startswith("D"):
        return "DTCS"
    if rx_tone == "None" and tx_tone == "None":
        return ""
    if rx_tone == "None":
        return "TSQL"
    return "Tone"


def calculate_tone_frequency(tone):
    """Calculate the Tone Frequency."""
    if tone != "None" and not tone.isalnum():
        return float(tone)
    return 88.5


def calculate_dtcs_code(tone):
    """Calculate the DTCS Code."""
    if tone.startswith("D"):
        return tone.lstrip("D").rstrip("I").rstrip("N")
    return 23


def determine_dtcs_polarity(rx_tone, tx_tone):
    """Determine the DTCS Polarity."""
    if rx_tone.endswith("I") or tx_tone.endswith("I"):
        return "RR"
    if rx_tone.endswith("N") or tx_tone.endswith("N"):
        return "NN"
    return "NN"


def determine_cross_mode(rx_tone, tx_tone):
    """Determine the Cross Mode."""
    if rx_tone.startswith("D") or tx_tone.startswith("D"):
        return "DTCS->DTCS"
    if rx_tone != "None" or tx_tone != "None":
        return TONE_TONE
    return TONE_TONE


def transform_chirp_row(row, channel_number):
    """Transform a single row into the target format for CHIRP."""
    return {
        **CHIRP_DEFAULT_VALUES,
        LOCATION: channel_number,
        NAME: row[CHANNEL_NAME],
        FREQUENCY: row[RX_FREQUENCY],
        DUPLEX: determine_duplex(row[TX_FREQUENCY], row[RX_FREQUENCY]),
        OFFSET: calculate_offset(row[TX_FREQUENCY], row[RX_FREQUENCY]),
        TONE: determine_tone(row[RX_TONE], row[TX_TONE]),
        RTONE_FREQ: calculate_tone_frequency(row[RX_TONE]),
        CTONE_FREQ: calculate_tone_frequency(row[TX_TONE]),
        DTCS_CODE: calculate_dtcs_code(row[TX_TONE]),
        DTCS_POLARITY: determine_dtcs_polarity(row[RX_TONE], row[TX_TONE]),
        RX_DTCS_CODE: calculate_dtcs_code(row[RX_TONE]),
        CROSS_MODE: determine_cross_mode(row[RX_TONE], row[TX_TONE]),
        MODE: "NFM" if row[BANDWIDTH_KHZ] == "12.5" else "FM",
        SKIP: "S" if row[ALL_SKIP] == "Yes" else "",
    }


# Main function
def transform_channels(operation, input_file, output_file, start_channel):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=GD77_FIELDNAMES if operation == "gd77" else CHIRP_FIELDNAMES)
            writer.writeheader()

            channel_number = start_channel + 1 if operation == "gd77" else start_channel
            for row in reader:
                try:
                    if operation == "gd77" or row["Channel Type"] == "Analogue":
                        transformed_row = (
                            transform_row(row, channel_number)
                            if operation == "gd77"
                            else transform_chirp_row(row, channel_number)
                        )
                        writer.writerow(transformed_row)
                        channel_number += 1
                except KeyError as e:
                    raise ValueError(f"Missing key {e} in input row: {row}")
                except ValueError as e:
                    raise ValueError(f"Invalid value in row {row}: {e}")
    except FileNotFoundError as e:
        raise ValueError(f"File not found: {e.filename}")
    except PermissionError as e:
        raise ValueError(f"Permission error: {e}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {e}")


# Entry point
if __name__ == "__main__":
    # Validate input arguments
    if len(sys.argv) > 5:
        print(
            "Error: Too many arguments provided. Usage: python opengd77-chirp-csv-coverter.py [input_file] [output_file] ["
            "start_channel]")
        sys.exit(1)

    # Assign values based on input or defaults
    operation = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OPERATION
    # Validate operation
    if operation not in VALID_OPERATIONS:
        print(f"Error: Invalid operation '{operation}'. Allowed operations are: {', '.join(VALID_OPERATIONS.keys())}.")
        sys.exit(1)

    # Retrieve default input and output files from the dictionary
    input_file_default = VALID_OPERATIONS[operation]["default_input_file"]
    output_file_default = VALID_OPERATIONS[operation]["default_output_file"]

    # Assign input and output files based on arguments or defaults
    input_file = sys.argv[2] if len(sys.argv) > 2 else input_file_default
    output_file = sys.argv[3] if len(sys.argv) > 3 else output_file_default
    
    start_channel = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_START_CHANNEL
    transform_channels(operation, input_file, output_file, start_channel)
