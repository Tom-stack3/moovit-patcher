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
- Google Maps SDK API key

### How to create your own API key

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project and attach a billing account. Maps Platform requires billing, though there's a free monthly allowance.
2. Under APIs & Services → Library, enable:
  * Maps SDK for Android
  * Geocoding API
  * Places API
  * Geolocation API
3. Under APIs & Services → Credentials, choose Create credentials → API key.

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
# Set env variable:
CUSTOM_GOOGLE_API_KEY="<your Google API key>"
# Run patcher:
python main.py -p ./moovit.apk -o moovitpatched.apk -gakey "$CUSTOM_GOOGLE_API_KEY"
```

## Testing / Installing

With exactly one device or emulator connected (`adb devices`), install and launch the patched APK:

```bash
python -m unittest tests.test_app_launch
```

This can also be used to install the `.apk` through `adb`.

## Credits

- [WhatsApp Patcher](https://github.com/Schwartzblat/WhatsAppPatcher/) by [@Schwartzblat](https://github.com/Schwartzblat)
  - Took a lot of utils from this code. Thank you!!

## Contributing

Ideas and contributions are always welcome. Please open an issue first for discussion.
