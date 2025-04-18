import csv
import logging
import sys
from typing import Dict, Any
from typing import Callable

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === GD77 FIELD CONSTANTS ===
CHANNEL_NUMBER = "Channel Number"
CHANNEL_NAME = "Channel Name"
CHANNEL_TYPE = "Channel Type"
RX_FREQUENCY = "Rx Frequency"
TX_FREQUENCY = "Tx Frequency"
BANDWIDTH_KHZ = "Bandwidth (kHz)"
COLOUR_CODE = "Colour Code"
TIME_SLOT = "Timeslot"
CONTACT = "Contact"
TG_LIST = "TG List"
DMR_ID = "DMR ID"
TS1_TA_TX = "TS1_TA_Tx"
TS2_TA_TX_ID = "TS2_TA_Tx ID"
RX_TONE = "RX Tone"
TX_TONE = "TX Tone"
SQUELCH = "Squelch"
POWER = "Power"
RX_ONLY = "Rx Only"
ZONE_SKIP = "Zone Skip"
ALL_SKIP = "All Skip"
TOT = "TOT"
VOX = "VOX"
NO_BEEP = "No Beep"
NO_ECO = "No Eco"
APRS = "APRS"
LATITUDE = "Latitude"
LONGITUDE = "Longitude"
USE_LOCATION = "Use Location"

# === CHIRP FIELD CONSTANTS ===
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
TSTEP = "TStep"
SKIP = "Skip"
COMMENT = "Comment"
URCALL = "URCALL"
RPT1CALL = "RPT1CALL"
RPT2CALL = "RPT2CALL"
DVCODE = "DVCODE"

# === OTHER CONSTANTS ===
TONE_TONE = "Tone->Tone"
ANALOGUE = "Analogue"
DIGITAL = "Digital"
DMR = "DMR"
NFM = "NFM"
FM = "FM"
DTCS = "DTCS"
TONE_STR = "Tone"
TSQL = "TSQL"
CROSS = "Cross"
DTCS_TO_DTCS = "DTCS->DTCS"
NONE = "None"
YES = "Yes"
NO = "No"
OFF = "Off"
DISABLED = "Disabled"
MASTER = "Master"
P1 = "P1"
P5 = "P5"
P6 = "P6"
P7 = "P7"
P8 = "P8"
P9 = "P9"

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

# Default values for fields not in the input format
GD77_DEFAULT_VALUES = {
    CHANNEL_TYPE: ANALOGUE,
    BANDWIDTH_KHZ: "25",
    COLOUR_CODE: "",
    TIME_SLOT: "",
    CONTACT: "",
    TG_LIST: "",
    DMR_ID: "",
    TS1_TA_TX: "",
    TS2_TA_TX_ID: "",
    RX_TONE: NONE,
    TX_TONE: NONE,
    SQUELCH: DISABLED,
    POWER: MASTER,
    RX_ONLY: NO,
    ZONE_SKIP: NO,
    ALL_SKIP: NO,
    TOT: "0",
    VOX: OFF,
    NO_BEEP: NO,
    NO_ECO: NO,
    APRS: NONE,
    LATITUDE: "0.128",
    LONGITUDE: "0.008",
    USE_LOCATION: NO
}

CHIRP_DEFAULT_VALUES = {
    TSTEP: "12.500",
    POWER: "50W",
    COMMENT: "",
    URCALL: "",
    RPT1CALL: "",
    RPT2CALL: "",
    DVCODE: ""
}

GD77_FIELDNAMES = [
    CHANNEL_NUMBER, CHANNEL_NAME, CHANNEL_TYPE, RX_FREQUENCY, TX_FREQUENCY,
    BANDWIDTH_KHZ, COLOUR_CODE, TIME_SLOT, CONTACT, TG_LIST, DMR_ID,
    TS1_TA_TX, TS2_TA_TX_ID, RX_TONE, TX_TONE, SQUELCH, POWER, RX_ONLY,
    ZONE_SKIP, ALL_SKIP, TOT, VOX, NO_BEEP, NO_ECO, APRS, LATITUDE,
    LONGITUDE, USE_LOCATION
]

CHIRP_FIELDNAMES = [
    LOCATION, NAME, FREQUENCY, DUPLEX, OFFSET, TONE, RTONE_FREQ,
    CTONE_FREQ, DTCS_CODE, DTCS_POLARITY, RX_DTCS_CODE, CROSS_MODE, MODE,
    TSTEP, SKIP, POWER, COMMENT, URCALL, RPT1CALL, RPT2CALL, DVCODE
]


# Helper functions
def calculate_tx_frequency(row):
    """Calculate Tx Frequency based on Duplex and Offset."""
    if row[DUPLEX] == "" or row[OFFSET] == "" or abs(float(row[OFFSET]) - 0.0) < 1e-9:
        return row[FREQUENCY]
    offset = float(row[OFFSET])
    frequency = float(row[FREQUENCY])
    return str(frequency + offset if row[DUPLEX] == "+" else frequency - offset)


def calculate_power(row):
    """Determine Power level based on the value in row['Power']."""  # docstring can keep 'Power'
    power = float(row[POWER].rstrip("W"))
    if power < 1.0:
        return P1
    elif 1.0 <= power < 2.0:
        return P5
    elif 2.0 <= power < 3.0:
        return P6
    elif 3.0 <= power < 4.0:
        return P7
    elif 4.0 <= power < 5.0:
        return P8
    elif row[POWER].rstrip("W") == "5.0":
        return P9
    return GD77_DEFAULT_VALUES[POWER]


def extract_polarity(value):
    """Extract polarity 'R' if 'II' is present, 'N' if 'NN' is present."""
    if "RR" in value:
        return "I"
    elif "NN" in value:
        return "N"
    return ""


def calculate_tone(row: Dict[str, Any], tone_type: str) -> str:
    """Calculate RX or TX Tone based on the Tone type."""
    if row[TONE] == DTCS:
        return f"D{row[DTCS_CODE]}{extract_polarity(row[DTCS_POLARITY])}"
    elif row[TONE] == TONE_STR:
        return row[f"{tone_type}ToneFreq"]
    elif row[TONE] == TSQL:
        return NONE
    elif row[TONE] == CROSS:
        if row[CROSS_MODE] == TONE_TONE:
            return row[f"{tone_type}ToneFreq"]
        elif tone_type == "r":
            return f"D{row[RX_DTCS_CODE]}{extract_polarity(row[DTCS_POLARITY])}"
        elif tone_type == "c":
            return f"D{row[DTCS_CODE]}{extract_polarity(row[DTCS_POLARITY])}"
    return NONE


def determine_channel_type(mode):
    if mode == DMR:
        return DIGITAL
    else:
        return ANALOGUE
    
    
def transform_row(row: Dict[str, Any], channel_number: int) -> Dict[str, Any]:
    """Transform a single row into the target format."""
    try:
        return {
            **GD77_DEFAULT_VALUES,
            CHANNEL_NUMBER: channel_number,
            CHANNEL_TYPE: determine_channel_type(row[MODE]),
            CHANNEL_NAME: row[NAME],
            BANDWIDTH_KHZ: 12.5 if row[MODE] == NFM else 25,
            RX_FREQUENCY: f"{float(row[FREQUENCY]):.5f}",
            TX_FREQUENCY: f"{float(calculate_tx_frequency(row)):.5f}",
            RX_TONE: calculate_tone(row, "r"),
            TX_TONE: calculate_tone(row, "c"),
            POWER: calculate_power(row),
            ALL_SKIP: YES if row[SKIP] == "S" else GD77_DEFAULT_VALUES[ALL_SKIP]
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
    if rx_tone != NONE and tx_tone != NONE and rx_tone != tx_tone:
        return CROSS
    if rx_tone.startswith("D") or tx_tone.startswith("D"):
        return DTCS
    if rx_tone == NONE and tx_tone == NONE:
        return ""
    if rx_tone == NONE:
        return TSQL
    return TONE_STR


def calculate_tone_frequency(tone):
    """Calculate the Tone Frequency."""
    if tone != NONE and tone != "" and not tone.isalnum():
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
        return DTCS_TO_DTCS
    if rx_tone != NONE or tx_tone != NONE:
        return TONE_TONE
    return TONE_TONE


def determine_mode(bandwidth, channel_type):
    """Determine the Mode based on Bandwidth and Channel Type."""
    if channel_type == DIGITAL:
        return DMR
    if bandwidth == "12.5":
        return NFM
    return FM

def determine_chirp_comment(row):
    if row[CHANNEL_TYPE] == DIGITAL:
        return f"DMR ID: {row[DMR_ID]}, TG List: {row[TG_LIST]}, Colour Code: {row[COLOUR_CODE]}, Timeslot: {row[TIME_SLOT]}, Contact: {row[CONTACT]}"
    else:
        return ""

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
        MODE: determine_mode(row[BANDWIDTH_KHZ], row[CHANNEL_TYPE]),
        SKIP: "S" if row[ALL_SKIP] == YES else "",
        COMMENT: determine_chirp_comment(row),
    }


def read_input_file(input_file: str):
    """Read the input CSV file and return a DictReader."""
    try:
        return csv.DictReader(open(input_file, 'r'))
    except FileNotFoundError as e:
        raise ValueError(f"File not found: {e.filename}")
    except PermissionError as e:
        raise ValueError(f"Permission error: {e}")


def write_output_file(output_file: str, fieldnames: list):
    """Open the output CSV file and return a DictWriter."""
    try:
        outfile = open(output_file, 'w', newline='')
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        return writer
    except PermissionError as e:
        raise ValueError(f"Permission error: {e}")


def process_row(row: dict, channel_number: int, transform_func: Callable):
    """Process a single row and return the transformed row."""
    try:
        return transform_func(row, channel_number)
    except KeyError as e:
        logging.error(f"Missing key {e} in row: {row}")
        raise
    except ValueError as e:
        logging.error(f"Invalid value in row: {row}")
        raise


def transform_channels(operation, input_file, output_file, start_channel):
    """Transform channels based on the operation."""
    reader = read_input_file(input_file)
    writer = write_output_file(output_file, GD77_FIELDNAMES if operation == "gd77" else CHIRP_FIELDNAMES)

    transform_func = transform_row if operation == "gd77" else transform_chirp_row
    channel_number = start_channel + 1 if operation == "gd77" else start_channel

    for row in reader:
        transformed_row = process_row(row, channel_number, transform_func)
        writer.writerow(transformed_row)
        channel_number += 1


def main():
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


if __name__ == "__main__":
    main()
