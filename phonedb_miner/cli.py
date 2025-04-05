"""
Command Line Interface for PhoneDB Miner

This module provides a command line interface for the PhoneDB Miner,
allowing extraction of device data from the PhoneDB website.
"""
import argparse
import os
import sys
from phonedb_miner.miners.devices_list_miner import ensure_directory, scrape_brand_devices
from phonedb_miner.miners.device_detail_miner import scrape_brand_device_details, load_device_list_from_file

def main():
    """
    Main function of the command line interface
    """
    parser = argparse.ArgumentParser(description='PhoneDB Miner - Scrape device information from PhoneDB')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    list_parser = subparsers.add_parser('list', help='Mine device list for a brand')
    list_parser.add_argument('brand', help='Brand name to scrape (e.g., Samsung, Apple, Xiaomi)')
    list_parser.add_argument('--update', action='store_true', help='Update existing list instead of recreating it')
    list_parser.add_argument('--output', help='Output directory for saving results (default: data/devices_list)')

    extract_parser = subparsers.add_parser('extract', help='Extract detailed information for devices of a brand')
    extract_parser.add_argument('brand', help='Brand name to extract device details for (e.g., Samsung, Apple, Xiaomi)')
    extract_parser.add_argument('--max', type=int, help='Maximum number of devices to process')
    extract_parser.add_argument('--update', action='store_true', help='Update existing details instead of extracting all devices')
    extract_parser.add_argument('--output', help='Output directory for saving results (default: data/device_detail_list)')
    extract_parser.add_argument('--input-file', help='Custom input file with device list (overrides brand selection)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    devices_list_dir = os.path.join('data', 'devices_list')
    device_detail_list_dir = os.path.join('data', 'device_detail_list')

    ensure_directory('data')
    ensure_directory(devices_list_dir)
    ensure_directory(device_detail_list_dir)

    if args.command == 'list':
        brand = args.brand
        brand = brand.capitalize()

        print(f"Starting PhoneDB Miner for brand: {brand}")

        output_dir = args.output if hasattr(args, 'output') and args.output else devices_list_dir
        ensure_directory(output_dir)

        devices_count = scrape_brand_devices(brand, args.update, output_dir)

        if args.update:
            print(f"PhoneDB mining update complete! Total {brand} devices in database: {devices_count}")
        else:
            print(f"PhoneDB mining complete! Collected {devices_count} {brand} devices.")

    elif args.command == 'extract':
        brand = args.brand
        brand = brand.capitalize()

        print(f"Starting PhoneDB Data Extraction for brand: {brand}")

        max_devices = args.max if hasattr(args, 'max') else None
        update_mode = args.update if hasattr(args, 'update') else False
        custom_input_file = args.input_file if hasattr(args, 'input_file') and args.input_file else None

        output_dir = args.output if hasattr(args, 'output') and args.output else device_detail_list_dir
        ensure_directory(output_dir)

        if custom_input_file:
            print(f"Using custom input file: {custom_input_file}")
            details_count = scrape_brand_device_details(
                brand,
                max_devices,
                update_mode,
                output_dir,
                devices_list_dir,
                custom_input_file=custom_input_file
            )
        else:
            details_count = scrape_brand_device_details(
                brand,
                max_devices,
                update_mode,
                output_dir,
                devices_list_dir
            )

        if details_count is not None:
            if update_mode:
                print(f"PhoneDB data extraction update complete for {brand} devices.")
            else:
                print(f"PhoneDB data extraction complete! Collected detailed information for {details_count} {brand} devices.")
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()