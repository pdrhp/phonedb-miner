﻿# phonedb-miner

A Python scraper for collecting smartphone information from PhoneDB.net.

## Features

- Modular structure with separate components for different mining tasks
- Command-line interface for easy device data collection
- Scrapes device information (id, name, URL, brand) from PhoneDB.net
- Extracts detailed device specifications from individual device pages
- Supports multiple brands (Samsung, Apple, Xiaomi, etc.)
- Filters devices released in the last 5 years
- Saves data in JSON format in an organized directory structure
- Incremental updates to add new devices without duplicating existing ones
- Resilient to network errors with automatic retries
- Anti-detection measures with randomized delays
- Batch saving for long-running extraction processes
- Custom input and output file paths

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Use the command-line interface:

```bash
# Show help
python phonedb-cli.py --help

# Show help for the list command
python phonedb-cli.py list --help

# Scrape devices for a specific brand (e.g., Samsung)
python phonedb-cli.py list Samsung

# Update existing device list with new devices (no duplicates)
python phonedb-cli.py list Samsung --update

# Output to a custom directory
python phonedb-cli.py list Samsung --output custom/path/to/output

# Show help for the extract command
python phonedb-cli.py extract --help

# Extract detailed information for devices of a brand
python phonedb-cli.py extract Samsung

# Extract details for a limited number of devices
python phonedb-cli.py extract Samsung --max 10

# Update existing device details (only extract new devices)
python phonedb-cli.py extract Samsung --update

# Output device details to a custom directory
python phonedb-cli.py extract Samsung --output custom/path/to/output

# Use a custom input file with device list
python phonedb-cli.py extract Samsung --input-file custom/path/to/devices.json
```

## Data Structure

### Device List

The script collects and saves the following basic information for each device:

```json
{
  "id": "12345",
  "name": "Samsung Galaxy S23",
  "url": "https://phonedb.net/index.php?m=device&id=12345&c=samsung_galaxy_s23",
  "brand": "Samsung"
}
```

### Device Details

The extraction process collects detailed information like:

```json
{
  "id": "12345",
  "name": "Samsung Galaxy S23",
  "brand": "Samsung",
  "url": "https://phonedb.net/index.php?m=device&id=12345&c=samsung_galaxy_s23",
  "scraped_date": "2023-11-21 15:30:45",
  "full_name": "Samsung Galaxy S23",
  "dimensions": "146.3 x 70.9 x 7.6 mm (5.76 x 2.79 x 0.30 in)",
  "weight": "167 g (5.89 oz)",
  "display": "6.1 inch / 155.0 mm Dynamic AMOLED, 1080 x 2340, 425 PPI, HDR10+",
  "chipset": "Qualcomm SM8550-AC Snapdragon 8 Gen 2 (4 nm)",
  "cpu": "1x 3.36 GHz Cortex-X3 & 2x 2.8 GHz Cortex-A715 & 2x 2.8 GHz Cortex-A710 & 3x 2.0 GHz Cortex-A510",
  "gpu": "Adreno 740",
  "os": "Android 13, One UI 5.1",
  "storage": "128 GB / 256 GB, UFS 3.1, not expandable",
  "ram": "8 GB, LPDDR5",
  "main_camera": "50 MP, f/1.8, 24mm (wide), 10 MP, f/2.4, 70mm (telephoto), 12 MP, f/2.2, 13mm (ultrawide)",
  "selfie_camera": "12 MP, f/2.2, 26mm (wide)",
  "battery": "3900 mAh",
  "images": [
    "https://phonedb.net/img/Samsung_Galaxy_S23_1.jpg",
    "https://phonedb.net/img/Samsung_Galaxy_S23_2.jpg"
  ]
}
```

## Directory Structure

- `phonedb_miner/` - Main package
  - `__init__.py` - Package initialization
  - `cli.py` - Command-line interface module
  - `miners/` - Mining module subpackage
    - `__init__.py` - Mining module initialization
    - `devices_list_miner.py` - Module for mining device lists
    - `device_detail_miner.py` - Module for extracting detailed device information
- `data/` - Data storage directory (created automatically)
  - `devices_list/` - Directory for device list JSON files
  - `device_detail_list/` - Directory for detailed device information
- `phonedb-cli.py` - CLI entry point script

## Features in Detail

### List Mining

- Extracts basic device information (name, id, url) from PhoneDB.net
- Filters to devices released in the last 5 years by default
- Supports incremental updates with `--update` flag
- Outputs to JSON format in a structured directory

### Detail Extraction

- Extracts comprehensive device specifications from individual device pages
- Processes devices in batches with auto-saving every 10 devices
- Random delays between requests (0.5-0.8 seconds) to avoid detection
- Update mode to only extract details for new devices
- Custom input file support for specialized device lists
- Custom output directory support

