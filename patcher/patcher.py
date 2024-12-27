import pathlib
from termcolor import cprint
import os
import glob
import importlib

exclude_imports = ["__init__.py", "Patch.py"]
include_patches = ["LiveLocationPatch"]


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
        for filename in glob.iglob(
            os.path.join(self.extracted_path, "**", "*.smali"), recursive=True
        ):
            if len(patches_to_find) == 0:
                break
            with open(filename, "r", encoding="utf8") as f:
                data = f.read()
            for patch in patches_to_find:
                if not patch.class_filter(data):
                    continue
                patch.class_data = data
                patch.class_path = filename
                patches_to_find.remove(patch)
                cprint(f"[+] Found {patch} class: {patch.class_path}", "green")
        for patch in self.patches:
            if patch.class_data is None:
                cprint(f"[-] Did not find {patch} class.", "red")

    def patch_classes(self):
        for patch in self.patches:
            if patch.class_data is None:
                continue
            cprint(patch.print_message, "green")
            with open(patch.class_path, "w") as f:
                f.write(patch.class_modifier(patch.class_data))
