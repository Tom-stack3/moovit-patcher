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
| Disable Taxi and Transit on Demand suggestions | ✅ |
| Remove "Join and Pay with Moovit" section | ✅ |
| Moovit+ enabled | ✅ |
| Analytics disabled | Partial (see below) |

### Disabled analytics

| What | Sent to | Patch |
| ---- | ------- | ----- |
| Analytics events, with the last known GPS location attached | Moovit (AWS Kinesis `AnalyticsStream`) | `DisableKinesisAnalyticsPatch` |
| Device fingerprint, battery/network/storage metrics, ad IDs | Moovit (AWS Kinesis `ServerStream`) | `DisableTelemetryMessagesPatch` |
| Marketing events, including trip origin and destination addresses | AppsFlyer, Braze, Facebook, Firebase | `DisableMarketingEventsPatch` |
| Install attribution, sessions | AppsFlyer | `DisableAppsFlyerPatch` |
| Events, user ID and properties, automatic events | Firebase Analytics | `DisableFirebaseAnalyticsPatch` |

Messages the app needs (push token, favorites, reports) are still sent.
Since AppsFlyer is never started, AppsFlyer (OneLink) deep links do not work.

Not disabled yet:
- Facebook SDK automatic app events (install, app activation).
- Braze SDK sessions, device data, user profile attributes and location (location collection is enabled in the app's Braze config).
- Firebase Crashlytics and Performance Monitoring.

## Requirements

- Python3
- Java
- Google Maps SDK API key

### How to create your own API key

The custom key is only needed to render the **map tiles**. Those are drawn by
Google Play Services (the official Maps SDK), which derives the
`X-Android-Cert` header from the installed app's signing certificate.
A value the app itself cannot set, so the re-signed APK is rejected with the original
key and must use your own.

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project and attach a billing account. Maps Platform requires billing, though there's a free monthly allowance.
2. Under APIs & Services → Library, enable:
  - Maps SDK for Android
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

Tested with Moovit 5.203.0.1812.

```bash
CUSTOM_GOOGLE_API_KEY="<your Google API key>"
python main.py -p ./moovit.apkm -o moovitpatched.apk -gakey "$CUSTOM_GOOGLE_API_KEY"
```

## Testing

With exactly one device or emulator connected (`adb devices`), install and launch the patched APK:

```bash
python -m unittest tests.test_app_launch
```

## Credits

- [APKEditor](https://github.com/REAndroid/APKEditor) by [@REAndroid](https://github.com/REAndroid), used to merge split APK bundles.
- [WhatsApp Patcher](https://github.com/Schwartzblat/WhatsAppPatcher/) by [@Schwartzblat](https://github.com/Schwartzblat)
  - Took a lot of utils from this code. Thank you!!

## Contributing

Ideas and contributions are always welcome. Please open an issue first for discussion.
