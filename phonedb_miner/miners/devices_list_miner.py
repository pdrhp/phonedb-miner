import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime, timedelta
import urllib3
import re
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RESULTS_PER_PAGE = 29
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_EMPTY_PAGES = 3
MIN_DELAY = 1
MAX_DELAY = 3

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

def scrape_phonedb_devices(brand, page=0):
    """
    Extracts devices from PhoneDB for a specific brand and page
    """
    url = "https://phonedb.net/index.php?m=device&s=query"

    result_lower_limit = page * RESULTS_PER_PAGE

    today = datetime.now()
    five_years_ago = today - timedelta(days=5*365)

    released_min = five_years_ago.strftime("%Y-%m-%d")
    released_max = today.strftime("%Y-%m-%d")

    form_data = {
        'brand': brand,
        'model': '',
        'released_min': released_min,
        'released_max': released_max,
        'cat': '131',
        'os_family': '1',
        'ram_type': '1',
        'd_type': '0',
        'p_dual': '0',
        'ts': '0',
        'tp': '0',
        'kb': '0',
        'usb_c': '0',
        'bt': '0',
        'radio_rx': '0',
        'c_flash': '0',
        'cd_sensor': '0',
        'c2_flash': '0',
        'b_build': '0',
        'result_lower_limit': str(result_lower_limit)
    }

    for field in ['width_min', 'width_max', 'height_min', 'height_max', 'depth_min', 'depth_max',
                 'depth_i_min', 'depth_i_max', 'mass_min', 'mass_max', 'mass_oz_min', 'mass_oz_max',
                 'sw_e[]', 'cpu_clk_min', 'cpu_clk_max', 'ram_cap_min', 'ram_cap_max', 'ram_cap_b',
                 'rom_cap_min', 'rom_cap_max', 'rom_cap_b', 'd_diag_i_min', 'd_diag_i_max', 'd_res',
                 'd_px_min', 'd_px_max', 'd_py_min', 'd_py_max', 'gpu_clk_min', 'gpu_clk_max',
                 'p_r[]', 'exp[]', 'wlan[]', 'nfc[]', 'gps[]', 'gps_e[]', 'c_px_min', 'c_px_max',
                 'c_py_min', 'c_py_max', 'c_focus[]', 'c_vres', 'c_e[]', 'c2_pn', 'c2_focus[]',
                 'b_cap_res_min', 'b_cap_res_max', 'country[]']:
        if '[]' in field:
            form_data[field] = '0'
        else:
            form_data[field] = ''

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://phonedb.net',
        'Referer': 'https://phonedb.net/index.php?m=device&s=query',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }

    try:
        response = make_request_with_retry(url, method="post", data=form_data, headers=headers, verify=False)

        if not response:
            print(f"Failed to fetch data for {brand} (page {page}) after {MAX_RETRIES} retries")
            return [], 0

        soup = BeautifulSoup(response.text, 'html.parser')

        devices = []
        total_results = 0

        result_info = soup.find('div', class_='content_desc')
        if result_info and 'results match' in result_info.text:
            result_text = result_info.text.strip()
            print(f"Found results info: {result_text}")

            match = re.search(r'(\d+)\s+results match', result_text)
            if match:
                total_results = int(match.group(1))
                print(f"Total results found: {total_results}")

        pagination_info = soup.find(text=re.compile(r'Result\s+Pages:'))
        if pagination_info:
            pagination_container = pagination_info.parent
            if pagination_container:
                page_links = pagination_container.find_all('a', href=re.compile(r'result_lower_limit='))
                if page_links:
                    last_page_link = page_links[-1]
                    match = re.search(r'result_lower_limit=(\d+)', last_page_link['href'])
                    if match:
                        last_page_offset = int(match.group(1))
                        estimated_total_results = last_page_offset + RESULTS_PER_PAGE
                        if estimated_total_results > total_results:
                            print(f"Updated total results from {total_results} to {estimated_total_results} based on pagination")
                            total_results = estimated_total_results

        device_blocks = soup.find_all('div', class_='content_block_title')

        if not device_blocks:
            print(f"No device blocks found for {brand} (page {page})")
            return [], total_results

        print(f"Found {len(device_blocks)} device blocks for {brand} (page {page})")

        for block in device_blocks:
            device_link = block.find('a')
            if not device_link:
                continue

            device_name = device_link.text.strip()
            device_url = "https://phonedb.net/" + device_link['href'] if device_link.has_attr('href') else None

            device_id = None
            if device_url:
                id_match = re.search(r'id=(\d+)', device_url)
                if id_match:
                    device_id = id_match.group(1)

            device_info = {
                "id": device_id,
                "name": device_name,
                "url": device_url,
                "brand": brand
            }

            devices.append(device_info)

        return devices, total_results

    except Exception as e:
        print(f"Error scraping {brand} (page {page}): {str(e)}")
        return [], 0

def save_devices_to_file(devices, brand, mode='w', output_dir=None):
    """
    Saves devices to a JSON file

    Args:
        devices: List of device dictionaries
        brand: Brand name
        mode: File open mode ('w' for write, 'a' for append)
        output_dir: Directory where device lists should be saved (default: data/devices_list)
    """
    if not devices:
        print(f"No devices to save for {brand}")
        return

    if output_dir is None:
        output_dir = os.path.join('data', 'devices_list')

    ensure_directory(output_dir)

    filename = os.path.join(output_dir, f"{brand.lower()}_devices.json")

    if mode == 'a' and os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_devices = json.load(f)
            except json.JSONDecodeError:
                existing_devices = []
                print(f"Warning: Existing file was invalid JSON. Creating a new one.")
                mode = 'w'

        existing_devices.extend(devices)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_devices, f, indent=4, ensure_ascii=False)

        print(f"Appended {len(devices)} devices to existing file. Total: {len(existing_devices)}")
        print(f"Updated {filename}")
    elif mode == 'w':
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(devices, f, indent=4, ensure_ascii=False)

        print(f"Created new file with {len(devices)} {brand} devices to {filename}")
    else:
        print(f"Writing {len(devices)} {brand} devices to {filename}")

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(devices, f, indent=4, ensure_ascii=False)

        print(f"Successfully saved {brand} devices to {filename}")

def scrape_brand_devices(brand, update_mode=False, output_dir=None):
    """
    Scrapes all devices for a specific brand by iterating through all result pages

    Args:
        brand: Brand name to be scraped (e.g. Samsung, Apple)
        update_mode: If True, updates the existing list instead of recreating it
        output_dir: Directory where device lists should be saved (default: data/devices_list)

    Returns:
        total_devices_collected: Total number of devices collected
    """
    total_devices_collected = 0
    total_new_devices = 0
    page = 0
    total_results = 1
    empty_pages_count = 0
    existing_devices = []
    existing_device_ids = set()

    print(f"Starting to scrape all {brand} devices...")

    if output_dir is None:
        output_dir = os.path.join('data', 'devices_list')

    ensure_directory(output_dir)
    filename = os.path.join(output_dir, f"{brand.lower()}_devices.json")

    if update_mode and os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_devices = json.load(f)
                existing_device_ids = {device.get('id') for device in existing_devices if device.get('id')}
                print(f"Loaded {len(existing_devices)} existing devices for updating.")
        except Exception as e:
            print(f"Error loading existing devices: {str(e)}")
            update_mode = False
            existing_devices = []
            existing_device_ids = set()

    if not update_mode and os.path.exists(filename):
        os.remove(filename)
        print(f"Removed existing file {filename}")

    while True:
        print(f"Scraping {brand} - Page {page+1}...")
        devices, total_results = scrape_phonedb_devices(brand, page)

        if not devices:
            empty_pages_count += 1
            print(f"No devices found on page {page+1}. Empty pages count: {empty_pages_count}")

            if page == 0:
                print(f"No devices found for {brand}")
                break
            elif total_devices_collected >= total_results:
                print(f"Reached the end of results. Total devices collected: {total_devices_collected}")
                break
            elif empty_pages_count >= MAX_EMPTY_PAGES:
                print(f"Reached maximum number of consecutive empty pages ({MAX_EMPTY_PAGES}). Stopping.")
                break
            else:
                page += 1
                continue
        else:
            empty_pages_count = 0

        if update_mode:
            new_devices = []
            for device in devices:
                if device.get('id') and device.get('id') not in existing_device_ids:
                    new_devices.append(device)
                    existing_device_ids.add(device.get('id'))

            if new_devices:
                existing_devices.extend(new_devices)
                print(f"Found {len(new_devices)} new devices on page {page+1}")
                total_new_devices += len(new_devices)

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(existing_devices, f, indent=4, ensure_ascii=False)

                print(f"Updated file with {len(existing_devices)} total devices")
        else:
            mode = 'w' if page == 0 else 'a'
            save_devices_to_file(devices, brand, mode, output_dir)

        total_devices_collected += len(devices)
        print(f"Collected {len(devices)} devices from page {page+1}. Total so far: {total_devices_collected}")

        if total_results and total_devices_collected >= total_results:
            print(f"Collected all {total_results} {brand} devices")
            break

        page += 1

        delay = random_delay()
        print(f"Waiting {delay:.2f} seconds before next page...")

    if update_mode:
        print(f"Finished updating. Found {total_new_devices} new devices. Total {brand} devices: {len(existing_devices)}")
        return len(existing_devices)
    else:
        print(f"Finished scraping. Total {brand} devices collected: {total_devices_collected}")
        return total_devices_collected