"""
GOTCHIPUSH: Handshake Uploader Tool

Author: Math0x
GitHub: https://github.com/fernstedt
License: MIT License

Description:
This script validates and uploads `.pcap` handshake files to the WPA-SEC service.
It supports features such as Dry Run mode, Force upload, and Validation checks.

Usage:
- python gotchipush.py          # Uploads handshakes
- python gotchipush.py --dry-run # Simulates the upload process
- python gotchipush.py --force   # Forces re-upload of files
"""

import os
import logging
import argparse
import requests
import json
import hashlib
from scapy.all import rdpcap, EAPOL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
HANDSHAKE_DIR = "/root/handshakes"  # Path to the handshake files
API_URL = "https://wpa-sec.stanev.org"  # WPA-SEC API base URL
API_KEY = "YOUR-KEY"  # <-- Set your API key here as per README instructions
UPLOADED_LOG = "/root/uploaded_handshakes.json"  # File to track uploaded handshakes


def ensure_trailing_slash(url):
    return url if url.endswith('/') else url + '/'


def calculate_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def is_valid_handshake(file_path):
    if os.path.getsize(file_path) == 0:
        logging.warning("File is empty: %s", file_path)
        return False

    try:
        with open(file_path, 'rb') as f:
            magic_bytes = f.read(4)
            if magic_bytes not in [b'\xd4\xc3\xb2\xa1', b'\xa1\xb2\xc3\xd4']:
                logging.warning("Invalid pcap magic bytes in file: %s", file_path)
                return False
    except Exception as e:
        logging.error("Error validating magic bytes for %s: %s", file_path, e)
        return False

    try:
        packets = rdpcap(file_path)
        for packet in packets:
            if packet.haslayer(EAPOL):
                return True
        logging.warning("No handshake data (EAPOL packets) found in file: %s", file_path)
        return False
    except Exception as e:
        logging.error("Error reading pcap file %s: %s", file_path, e)
        return False


def load_uploaded_files(log_file):
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as file:
                return set(json.load(file))
        except json.JSONDecodeError:
            logging.warning("Uploaded log file is corrupt. Starting fresh.")
    return set()


def save_uploaded_files(log_file, uploaded_files):
    with open(log_file, 'w') as file:
        json.dump(list(uploaded_files), file)


def upload_to_wpasec(file_path, api_url, api_key, dry_run=False, timeout=30):
    if dry_run:
        logging.info("[DRY RUN] File %s would be uploaded.", file_path)
        return True

    with open(file_path, 'rb') as file_to_upload:
        cookie = {'key': api_key}
        files = {'file': file_to_upload}

        try:
            response = requests.post(api_url, cookies=cookie, files=files, timeout=timeout)
            if response.status_code == 200:
                if 'already submitted' in response.text:
                    logging.info("File %s was already submitted.", file_path)
                    return False
                logging.info("Successfully uploaded: %s", file_path)
                return True
            else:
                logging.error("Failed to upload %s: HTTP %s - %s", file_path, response.status_code, response.text)
                return False
        except requests.exceptions.RequestException as e:
            logging.error("Request exception while uploading %s: %s", file_path, e)
            return False


def main():
    parser = argparse.ArgumentParser(description="GOTCHIPUSH: Handshake Uploader and Validator")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Simulate the upload without sending files")
    parser.add_argument("-v", "--validate-upload", action="store_true", help="Validate handshakes and upload status")
    parser.add_argument("-f", "--force", action="store_true", help="Force upload even if already uploaded")

    args = parser.parse_args()

    if not API_KEY:
        logging.error("API key is not set. Please configure the script with your API key.")
        return

    if not os.path.exists(HANDSHAKE_DIR):
        logging.error("Handshake directory %s does not exist.", HANDSHAKE_DIR)
        return

    api_url = ensure_trailing_slash(API_URL)
    uploaded_files = load_uploaded_files(UPLOADED_LOG)
    handshake_files = [
        os.path.join(HANDSHAKE_DIR, file)
        for file in os.listdir(HANDSHAKE_DIR)
        if file.endswith('.pcap')
    ]

    if not handshake_files:
        logging.info("No handshake files found in the directory.")
        return

    for handshake in handshake_files:
        file_hash = calculate_file_hash(handshake)
        if file_hash in uploaded_files and not args.force:
            logging.info("Skipping already uploaded file: %s", handshake)
            continue

        if not is_valid_handshake(handshake):
            logging.warning("Invalid handshake file (skipped): %s", handshake)
            continue

        if upload_to_wpasec(handshake, api_url, API_KEY, args.dry_run):
            uploaded_files.add(file_hash)

    save_uploaded_files(UPLOADED_LOG, uploaded_files)
    logging.info("Upload process completed.")


if __name__ == "__main__":
    main()
