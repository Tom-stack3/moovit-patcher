# Moovit Patcher

Apply patches to Moovit APK.
The content provided is for educational and informational purposes only.

## Features

|  Feature | Availability |
| -------- | ------------ |
| Live Location enabled | WP |
| Moovit+ enabled | WP |
| Ads disabled | WP |
| Analytics disabled | WP |

## Requirements

- Python3
- Java

## Installation

```bash
git clone https://github.com/Tom-stack3/moovit-patcher.git
cd moovit-patcher
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py -p ./moovit.apk -o moovitpatched.apk
```

## Credits

- [WhatsApp Patcher](https://github.com/Schwartzblat/WhatsAppPatcher/) by [@Schwartzblat](https://github.com/Schwartzblat)
    - Took a lot of utils from this code. Thank you!!
