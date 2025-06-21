# Moovit Patcher

Apply patches to Moovit APK, for educational purposes only.

> DISCLAIMER: This project is not affiliated with Moovit.\
> This project is intended for educational and informational purposes only.

## Features

|  Feature | Availability |
| -------- | ------------ |
| Live Location enabled | ✅ |
| Ads disabled | ✅ |
| Signature Verifier Bypass | ✅ |
| Disable Taxi suggestions | ✅ |
| Remove "Join and Pay with Moovit" section | ✅ |
| Remove bottom Moovit+ banner | ✅ |
| Moovit+ enabled | WIP |
| Analytics disabled | WIP |

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
CUSTOM_GOOGLE_API_KEY="<your Google API key>
python main.py -p ./moovit.apk -o moovitpatched.apk -gakey "$CUSTOM_GOOGLE_API_KEY"
```

## Credits

- [WhatsApp Patcher](https://github.com/Schwartzblat/WhatsAppPatcher/) by [@Schwartzblat](https://github.com/Schwartzblat)
  - Took a lot of utils from this code. Thank you!!

## Contributing

Ideas and contributions are always welcome. Please open an issue first for discussion.
