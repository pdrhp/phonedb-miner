import argparse
import os
import sys
from phonedb_miner.miners.devices_list_miner import ensure_directory, scrape_brand_devices

def main():
    """
    Main function of the command line interface
    """
    parser = argparse.ArgumentParser(description='PhoneDB Miner - Scrape device information from PhoneDB')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    list_parser = subparsers.add_parser('list', help='Mine device list for a brand')
    list_parser.add_argument('brand', help='Brand name to scrape (e.g., Samsung, Apple, Xiaomi)')
    list_parser.add_argument('--update', action='store_true', help='Update existing list instead of recreating it')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ensure_directory('data')
    ensure_directory(os.path.join('data', 'devices_list'))

    if args.command == 'list':
        brand = args.brand
        brand = brand.capitalize()

        print(f"Starting PhoneDB Miner for brand: {brand}")

        devices_count = scrape_brand_devices(brand, args.update)

        if args.update:
            print(f"PhoneDB mining update complete! Total {brand} devices in database: {devices_count}")
        else:
            print(f"PhoneDB mining complete! Collected {devices_count} {brand} devices.")

if __name__ == "__main__":
    main()