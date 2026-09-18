"""
Installs the patched APK on the single connected adb device and checks the app launches.

Usage (from the repo root, with a device/emulator connected):
    python -m unittest tests.test_app_launch
"""
import os
import subprocess
import time
import unittest

APK_PATH = os.environ.get("APK_PATH", "moovitpatched.apk")
PACKAGE_NAME = "com.tranzmate"


def adb(*args):
    return subprocess.run(
        ["adb", *args], capture_output=True, text=True, timeout=5 * 60
    )


class TestAppLaunch(unittest.TestCase):
    def test_install_and_launch(self):
        lines = adb("devices").stdout.strip().splitlines()[1:]
        devices = [line.split()[0] for line in lines if line.endswith("\tdevice")]
        self.assertEqual(len(devices), 1, f"Expected exactly one adb device, got: {lines}")

        result = adb("install", "-r", APK_PATH)
        self.assertIn("Success", result.stdout, result.stdout + result.stderr)

        adb("logcat", "-c")
        result = adb(
            "shell", "monkey", "-p", PACKAGE_NAME,
            "-c", "android.intent.category.LAUNCHER", "1",
        )
        self.assertIn("Events injected: 1", result.stdout, result.stdout + result.stderr)

        # Give the app time to start (and to crash, if it is going to).
        time.sleep(15)
        pid = adb("shell", "pidof", PACKAGE_NAME).stdout.strip()
        crash_log = adb("logcat", "-d", "-b", "crash").stdout
        self.assertTrue(pid, f"{PACKAGE_NAME} is not running after launch.\n{crash_log}")
        self.assertNotIn(f"Process: {PACKAGE_NAME}", crash_log, crash_log)


if __name__ == "__main__":
    unittest.main()
