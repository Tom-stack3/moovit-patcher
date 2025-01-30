import pathlib
from termcolor import cprint
import os
import glob
import importlib
from .patches.LPatch import LPatch

exclude_imports = ["__init__.py", "Patch.py"]
include_patches = ["LiveLocationPatch", "BypassSignaturePatch", "DisableAdsPatch"]


class Patcher:
    def __init__(self, extracted_path):
        self.extracted_path = extracted_path
        self.patches = []
        current_dir = pathlib.Path(__file__).parent / "patches"
        for path in glob.iglob(os.path.join(current_dir, "*.*")):
            if os.path.basename(path) in exclude_imports:
                continue
            if include_patches and pathlib.Path(path).stem not in include_patches:
                continue
            module_name = "patcher.patches." + pathlib.Path(path).stem
            module = importlib.import_module(module_name, module_name)
            inner_class = (
                getattr(module, dir(module)[0])
                if dir(module)[0] != "Patch"
                else getattr(module, dir(module)[1])
            )
            self.patches.append(inner_class(self.extracted_path))

    def find_classes(self):
        patches_to_find = self.patches.copy()
        for patch in patches_to_find:
            cprint(f"[+] Searching for {patch} classes...", "yellow")
            for filename in glob.iglob(
                os.path.join(self.extracted_path, "**", "*.smali"), recursive=True
            ):
                with open(filename, "r", encoding="utf8") as f:
                    data = f.read()
                if not patch.class_filter(data):
                    continue

                patch.class_data.append(data)
                patch.class_path.append(filename)
                if not patch.is_multi_class:
                    break

            cprint(f"[+] Found {patch} class: {patch.class_path}", "green")

        for patch in self.patches:
            if len(patch.class_data) == 0:
                cprint(f"[-] Did not find {patch} classes.", "red")

    def patch_classes(self):
        for patch in self.patches:
            if len(patch.class_data) == 0:
                continue
            cprint(patch.print_message, "green")
            for class_data, class_path in zip(patch.class_data, patch.class_path):
                with open(class_path, "w") as f:
                    f.write(patch.class_modifier(class_data, class_path))
                cprint(f"[+] Patched {patch} class: {class_path}", "green")
        cprint("[+] Finished patching classes.", "green")

    def patch_resources(self):
        filename = os.path.join(self.extracted_path, "resources.arsc")
        lp = LPatch(self.extracted_path)
        if os.path.exists(filename):
            cprint("[+] Patching resources.arsc...", "green")
            with open(filename, "rb") as f:
                lp.class_data = f.read()
            with open(filename, "wb") as f:
                f.write(lp.class_modifier(lp.class_data, filename))
            cprint("[+] Finished patching resources.arsc.", "green")
