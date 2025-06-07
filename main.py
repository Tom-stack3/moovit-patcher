import argparse
import os
from termcolor import cprint
from patcher.extractor import Extractor
from patcher.patcher import Patcher
from timeit import default_timer


def main():
    start = default_timer()
    parser = argparse.ArgumentParser(description="Patch Moovit APK")
    parser.add_argument("-path", "-p", dest="path", type=str, required=True)
    parser.add_argument(
        "-output", "-o", dest="output", type=str, default="patched.apk"
    )
    parser.add_argument(
        "--temp-path", dest="temp_path", type=str, default="./extracted"
    )
    parser.add_argument(
        "--no-patching", "-np", action="store_true", default=False,
        help="Only extract and compile the APK, do not apply patches."
    )
    parser.add_argument(
        "--skip-decompile", "-sd", action="store_true", default=False,
        help="Skip decompiling the APK, use what is already in the temp path."
    )
    parser.add_argument(
        "--skip-compile", "-sc", action="store_true", default=False,
        help="Skip compiling back the APK"
    )
    parser.add_argument(
        "--skip-prompts", "-sp", action="store_true", default=False,
        help="Skip prompts waiting for user input"
    )
    args = parser.parse_args()
    path = args.path
    if not os.path.exists(path) or not os.access(path, os.R_OK):
        cprint(f"[+] Unable to access file: {path}", color="red")
        exit(-1)
    if not path.endswith(".apk") or not args.output.endswith(".apk"):
        cprint("[+] Input path and output paths should be a APK files", color="red")
        exit(-1)
    extractor = Extractor(path, args.output, args.temp_path)
    if not args.skip_decompile:
        extractor.extract_apk()
    patcher = Patcher(extractor.temp_path)
    patcher.find_classes()
    if not args.no_patching:
        patcher.patch_classes()
        patcher.patch_resources()
    if not args.skip_compile:
        if not args.skip_prompts:
            input("Press Enter to continue to compilation back and signing stage...")
        extractor.compile_smali()
        extractor.sign_apk()
    print(f"Took {default_timer()-start} seconds to complete the run.")


if __name__ == "__main__":
    main()
