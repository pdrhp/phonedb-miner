"""
Device Detail Miner for PhoneDB

This module contains functions to extract detailed device information from individual device pages.
It uses the device list JSON files previously created to get the URLs of each device.
"""
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
import random
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_RETRIES = 3
RETRY_DELAY = 2
MIN_DELAY = 0.5
MAX_DELAY = 0.8
SAVE_BATCH_SIZE = 10

def ensure_directory(directory_path):
    """
    Checks if the directory exists and creates it if it doesn't
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")

def random_delay():
    """
    Adds a random delay to avoid bot detection
    """
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)
    return delay

def make_request_with_retry(url, method="get", **kwargs):
    """
    Makes an HTTP request with automatic retry in case of failure
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            if method.lower() == "post":
                response = requests.post(url, **kwargs)
            else:
                response = requests.get(url, **kwargs)

            if response.status_code == 200:
                return response

            print(f"Request failed with status code {response.status_code}. Retrying...")
        except Exception as e:
            print(f"Request failed with error: {str(e)}. Retrying...")

        retries += 1
        time.sleep(RETRY_DELAY * (2 ** retries))

    return None

def load_device_list(brand, devices_list_dir=None):
    """
    Loads the device list JSON file for a specific brand

    Args:
        brand: Brand name
        devices_list_dir: Directory where device lists are stored (default: data/devices_list)

    Returns:
        List of device dictionaries or None if file doesn't exist
    """
    if devices_list_dir is None:
        devices_list_dir = os.path.join('data', 'devices_list')

    filename = os.path.join(devices_list_dir, f"{brand.lower()}_devices.json")

    if not os.path.exists(filename):
        print(f"Error: Device list file for {brand} does not exist at {filename}")
        print(f"Please run 'python phonedb-cli.py list {brand}' first to create the device list")
        return None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            devices = json.load(f)
            print(f"Loaded {len(devices)} devices from {filename}")
            return devices
    except Exception as e:
        print(f"Error loading device list: {str(e)}")
        return None

def load_existing_details(brand, output_dir=None):
    """
    Loads existing device details for a brand if available

    Args:
        brand: Brand name
        output_dir: Directory where device details are stored (default: data/device_detail_list)

    Returns:
        Dictionary mapping device IDs to their details, or empty dict if no file exists
    """
    if output_dir is None:
        output_dir = os.path.join('data', 'device_detail_list')

    filename = os.path.join(output_dir, f"{brand.lower()}_devices.json")

    if not os.path.exists(filename):
        print(f"No existing device details file found for {brand}")
        return {}, []

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            details_list = json.load(f)

            details_map = {detail.get('id'): detail for detail in details_list if detail.get('id')}
            print(f"Loaded {len(details_map)} existing device details for {brand}")
            return details_map, details_list
    except Exception as e:
        print(f"Error loading existing device details: {str(e)}")
        return {}, []

def extract_device_details(soup, device_url, device_id):
    """
    Extracts detailed information from a device page

    Args:
        soup: BeautifulSoup object of the device page
        device_url: URL of the device page
        device_id: ID of the device

    Returns:
        Dictionary with device details
    """
    details = {
        "id": device_id,
        "url": device_url,
        "scraped_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    title = soup.find('title')
    if title:
        title_text = title.text.strip()
        title_parts = title_text.split('|')
        if len(title_parts) > 0:
            details["full_name"] = title_parts[0].strip()

    table_rows = soup.find_all('tr')

    for row in table_rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            field_name_cell = cells[0]
            field_value_cell = cells[1]

            field_name_tag = field_name_cell.find('strong')
            if not field_name_tag:
                continue

            field_name = field_name_tag.text.strip()

            field_value = field_value_cell.text.strip()

            key = field_name.lower().replace(' ', '_')

            details[key] = field_value


    images = []
    img_tags = soup.find_all('img', class_='device_image')
    for img in img_tags:
        if img.has_attr('src'):
            img_url = img['src']
            if not img_url.startswith('http'):
                img_url = f"https://phonedb.net/{img_url}"
            images.append(img_url)

    if images:
        details["images"] = images

    return details

def scrape_device_details(device):
    """
    Scrapes detailed information for a single device

    Args:
        device: Device dictionary with id, name, url, and brand

    Returns:
        Dictionary with detailed device information
    """
    if not device.get('url'):
        print(f"Error: Device {device.get('name')} has no URL")
        return None

    url = device['url']
    device_id = device.get('id')

    print(f"Scraping details for device: {device.get('name')} (ID: {device_id})")

    delay = random_delay()
    print(f"Waiting {delay:.2f} seconds before request...")

    response = make_request_with_retry(url, verify=False)
    if not response:
        print(f"Failed to fetch device details from {url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    details = extract_device_details(soup, url, device_id)

    details['name'] = device.get('name')
    details['brand'] = device.get('brand')

    return details

def save_device_details(device_details, brand, output_dir=None, is_partial=False):
    """
    Saves device details to a JSON file

    Args:
        device_details: List of device detail dictionaries
        brand: Brand name
        output_dir: Directory where device details should be saved (default: data/device_detail_list)
        is_partial: If True, indicates this is a partial save during processing
    """
    if not device_details:
        print(f"No device details to save for {brand}")
        return

    if output_dir is None:
        output_dir = os.path.join('data', 'device_detail_list')

    ensure_directory(output_dir)

    filename = os.path.join(output_dir, f"{brand.lower()}_devices.json")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(device_details, f, indent=4, ensure_ascii=False)

    if is_partial:
        print(f"Saved partial batch of {len(device_details)} detailed devices to {filename}")
    else:
        print(f"Successfully saved {len(device_details)} detailed devices to {filename}")

def load_device_list_from_file(file_path):
    """
    Loads a device list from a custom JSON file

    Args:
        file_path: Path to the JSON file containing device list

    Returns:
        List of device dictionaries or None if file doesn't exist or is invalid
    """
    if not os.path.exists(file_path):
        print(f"Error: Custom device list file does not exist at {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            devices = json.load(f)
            print(f"Loaded {len(devices)} devices from custom file: {file_path}")
            return devices
    except Exception as e:
        print(f"Error loading custom device list: {str(e)}")
        return None

def scrape_brand_device_details(brand, max_devices=None, update_mode=False, output_dir=None, devices_list_dir=None, custom_input_file=None):
    """
    Scrapes detailed information for all devices of a specific brand

    Args:
        brand: Brand name
        max_devices: Maximum number of devices to scrape (None for all)
        update_mode: If True, only scrape devices that don't already have details
        output_dir: Directory where device details should be saved (default: data/device_detail_list)
        devices_list_dir: Directory where device lists are stored (default: data/devices_list)
        custom_input_file: Optional path to a custom JSON file with device list

    Returns:
        Number of devices scraped or None if an error occurred
    """
    print(f"Starting to scrape detailed information for {brand} devices...")

    if custom_input_file:
        devices = load_device_list_from_file(custom_input_file)
    else:
        devices = load_device_list(brand, devices_list_dir)

    if not devices:
        return None

    if output_dir is None:
        output_dir = os.path.join('data', 'device_detail_list')

    existing_details_map = {}
    existing_details_list = []
    if update_mode:
        existing_details_map, existing_details_list = load_existing_details(brand, output_dir)
        print(f"Update mode enabled: Will only scrape devices not already in the database")

    num_devices = len(devices)
    if max_devices and max_devices < num_devices:
        print(f"Limiting scraping to {max_devices} devices out of {num_devices}")
        devices = devices[:max_devices]
    else:
        print(f"Scraping all {num_devices} devices")

    details_list = existing_details_list if update_mode else []
    new_devices_count = 0
    skipped_count = 0
    success_count = 0

    for i, device in enumerate(devices):
        device_id = device.get('id')

        if update_mode and device_id in existing_details_map:
            print(f"Skipping device {i+1}/{len(devices)}: {device.get('name')} (ID: {device_id}) - already in database")
            skipped_count += 1
            continue

        print(f"Processing device {i+1}/{len(devices)}: {device.get('name')}")

        details = scrape_device_details(device)
        if details:
            if update_mode:
                details_list.append(details)
                new_devices_count += 1
            else:
                details_list.append(details)

            success_count += 1

        if success_count > 0 and success_count % SAVE_BATCH_SIZE == 0:
            print(f"Reached {success_count} processed devices, saving partial results...")
            save_device_details(details_list, brand, output_dir, is_partial=True)

        if i < len(devices) - 1:
            delay = random_delay()
            print(f"Waiting {delay:.2f} seconds before next device...")

    save_device_details(details_list, brand, output_dir)

    print(f"Finished scraping detailed information.")
    print(f"Successfully processed {success_count} of {len(devices)} devices.")

    if update_mode:
        print(f"Added {new_devices_count} new devices, skipped {skipped_count} existing devices.")
        print(f"Total devices in database: {len(details_list)}")

    return success_count