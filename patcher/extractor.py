import pathlib
import shutil
import subprocess
import os
from termcolor import cprint
import zipfile
from .signing import get_signing_certificate

BUNDLE_EXTENSIONS = (".apkm", ".apks", ".xapk")


class Extractor:
    def __init__(self, path: str, output_path: str, temp_path: str = "./extracted"):
        self.apk_path = path
        self.temp_path = temp_path
        self.output_path = output_path

    def merge_bundle(self):
        """
        Merge a split APK bundle (base.apk + config splits) into a single APK.
        Moovit is only published as a bundle.
        """
        merged_path = os.path.splitext(self.apk_path)[0] + "-merged.apk"
        if os.path.exists(merged_path):
            os.remove(merged_path)
        apk_editor = pathlib.Path(__file__).parent.parent / "bin" / "APKEditor-1.4.9.jar"
        cprint("[+] Merging the APK bundle with APKEditor.", "green")
        subprocess.check_call(
            ["java", "-jar", str(apk_editor), "m", "-i", self.apk_path, "-o", merged_path],
            timeout=20 * 60,
        )
        self.apk_path = merged_path

    def extract_apk(self):
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)
        if self.apk_path.endswith(BUNDLE_EXTENSIONS):
            self.merge_bundle()
        apktool_base_path = pathlib.Path(__file__).parent.parent / "bin"
        apk_tool = apktool_base_path / "apktool_2.7.0.jar"
        cprint("[+] Running apktool to decompile the apk.", "green")
        subprocess.check_call(
            [
                "java",
                "-jar",
                str(apk_tool),
                "-q",
                "d",
                "-r",
                "--output",
                str(self.temp_path),
                str(self.apk_path),
            ],
            timeout=20 * 60,
        )
        cprint("[+] Apktool decompiled the apk.", "green")
        self.extract_dex()
        self.extract_signing_certificate()

    def extract_signing_certificate(self):
        # Kept under original/, which apktool does not pack back into the APK.
        cert_path = os.path.join(self.temp_path, "original", "signing-cert.der")
        os.makedirs(os.path.dirname(cert_path), exist_ok=True)
        with open(cert_path, "wb") as f:
            f.write(get_signing_certificate(self.apk_path))

    def extract_dex(self):
        with zipfile.ZipFile(self.apk_path) as z:
            z.extract("classes.dex", self.temp_path)

    def compile_smali(self):
        if os.path.exists(self.temp_path + "/classes.dex"):
            os.remove(self.temp_path + "/classes.dex")
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        apktool_base_path = pathlib.Path(__file__).parent.parent / "bin"
        apk_tool = apktool_base_path / "apktool_2.7.0.jar"
        command = [
            "java",
            "-jar",
            str(apk_tool),
            "-q",
            "build",
            "--use-aapt2",
            self.temp_path,
            "--output",
            self.output_path,
        ]
        cprint("[+] Compiling smali with apktool", "green")
        subprocess.check_call(command, timeout=20 * 60)
        cprint("[+] Smali compiled successfully", "green")
        # shutil.rmtree(self.temp_path) # TODO: Remove

    def sign_apk(self):
        uber_signer = (
            pathlib.Path(__file__).parent.parent / "bin" / "uber-apk-signer-1.2.1.jar"
        )
        command = [
            "java",
            "-jar",
            str(uber_signer),
            "--apks",
            self.output_path,
        ]
        cprint("[+] Signing the apk with uber apk signer", "green")
        subprocess.check_call(command, timeout=20 * 60)
        cprint("[+] Finished successfully", "green")
        os.remove(self.output_path)
        os.rename(
            f'{self.output_path.removesuffix(".apk")}-aligned-debugSigned.apk',
            self.output_path,
        )
