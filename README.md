# phonedb-miner

A Python scraper for collecting smartphone information from PhoneDB.net.

## Features

- Modular structure with separate components for different mining tasks
- Command-line interface for easy device data collection
- Scrapes device information (id, name, URL, brand) from PhoneDB.net
- Supports multiple brands (Samsung, Apple, Xiaomi, etc.)
- Filters devices released in the last 5 years
- Saves data in JSON format in an organized directory structure
- Incremental updates to add new devices without duplicating existing ones
- Resilient to network errors with automatic retries
- Anti-detection measures with randomized delays

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
```

## Data Structure

The script collects and saves the following information for each device:

```json
{
  "id": "12345",
  "name": "Samsung Galaxy S23",
  "url": "https://phonedb.net/index.php?m=device&id=12345&c=samsung_galaxy_s23",
  "brand": "Samsung"
}
```

## Directory Structure

- `phonedb_miner/` - Main package
  - `__init__.py` - Package initialization
  - `cli.py` - Command-line interface module
  - `miners/` - Mining module subpackage
    - `__init__.py` - Mining module initialization
    - `devices_list_miner.py` - Module for mining device lists
- `data/` - Data storage directory (created automatically)
  - `devices_list/` - Directory for device list JSON files
- `phonedb-cli.py` - CLI entry point script

## Future Extensions

The modular structure allows for easy extension with new functionality:

- Device detail mining from individual device pages
- Processor information mining
- Operating system information mining
- Exporting data to different formats

## License

MIT
