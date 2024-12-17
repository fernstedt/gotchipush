# GOTCHIPUSH: Handshake Uploader Tool

This is a Python tool for uploading `.pcap` handshake files to the [WPA-SEC](https://wpa-sec.stanev.org) service. It validates, uploads, and manages handshakes efficiently, with features like **Dry Run mode**, **Force upload**, and **Validation checks**.

---
<!-- ## Creator Info
Tool developed by:Math0x  
GitHub: https://github.com/fernstedt  

-->

## Configuration

The only required configuration is the **API Key**, which you can retrieve from your [WPA-SEC account](https://wpa-sec.stanev.org).

1. Open the `gotchipush.py` script.
2. Set the API key in the following line:

   ```python
   API_KEY = "your_api_key_here"
   ```

> **Note:** The rest of the configuration options (like paths and URLs) are already set and should not be changed.

---

## Usage

### 1. Upload Handshakes
Upload all valid `.pcap` handshakes from the `handshakes` directory:

```bash
python gotchipush.py
```

### 2. Dry Run Mode
Simulate the upload process without sending any files:

```bash
python gotchipush.py --dry-run
```

### 3. Force Upload
Force upload all `.pcap` files, even if they were previously uploaded:

```bash
python gotchipush.py --force
```

### 4. Validate Handshakes
Validate the `.pcap` files in the `handshakes` directory and check their upload status:

```bash
python gotchipush.py --validate-upload
```

### Combine Options
- **Dry Run + Force Upload** (Simulates forced uploads):
   ```bash
   python gotchipush.py --dry-run --force
   ```

---

## Example Directory Structure

```bash
/root/
│
├── handshakes/                # Directory containing .pcap files
│   ├── handshake1.pcap
│   ├── handshake2.pcap
│   └── ...
│
├── gotchipush.py              # The main upload script
└── uploaded_handshakes.json   # Auto-generated file tracking uploaded handshakes
```

---

## Validation Process

The tool validates `.pcap` files using the following checks:

1. **File Size Check**:  
   Ensures the file is not empty.

2. **Magic Digits Check**:  
   Verifies the file starts with correct **magic bytes** for `.pcap` files:  
   - `d4 c3 b2 a1` (Little Endian)  
   - `a1 b2 c3 d4` (Big Endian)  

   These bytes confirm the file format conforms to the `.pcap` standard.

3. **EAPOL Packet Check**:  
   Scans the file for **EAPOL (Extensible Authentication Protocol over LAN)** packets, which indicate the presence of a valid WPA/WPA2 handshake.

If any of these checks fail, the file will be marked as **invalid** and skipped during the upload process.

---

## Logging

The tool logs all actions (validation, uploads, skips, etc.) in real-time to the console. If you need persistent logs, redirect output to a file:

```bash
python gotchipush.py > upload.log 2>&1
```

---

## Notes

- Handshake files that are invalid or missing EAPOL packets will be skipped.
- If `uploaded_handshakes.json` becomes corrupted, it will automatically reset to avoid issues.

---

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to suggest improvements.

---

## License

This project is licensed under the **GPL-3.0 License**.
