from ..Patch import Patch
import glob
import os
import re


class DisableFirebasePerformancePatch(Patch):
    """
    Patch to deactivate Firebase Performance Monitoring.

    Making ConfigResolver.getIsServiceCollectionDeactivated() return true, as if the
    "firebase_performance_collection_deactivated" manifest flag was set.
    Deactivation wins over every other setting (manifest, shared preferences, remote config).
    We are looking for the ConfigResolver class:
    .method public final f()Ljava/lang/Boolean;
    from: pq3.smali
    It reads the ConfigurationConstants$CollectionDeactivated flag (zq3.smali).
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+final\s+\w+\(\)Ljava/lang/Boolean;\s*(
        (?:(?!\.end\s+method).)*?
        const-class\s+\w+,\s+(L[\w/$]+;)
        .*?
        )\.end\s+method
        """,
        re.VERBOSE | re.DOTALL,
    )
    FLAG_RE = re.compile(r'const-string\s+\w+,\s+"firebase_performance_collection_deactivated"')
    METHOD_REPLACE = """
    .locals 1
    sget-object v0, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    return-object v0
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Firebase Performance patch..."

    def is_deactivated_flag(self, class_name: str) -> bool:
        relative = class_name[1:-1] + ".smali"
        for path in glob.glob(os.path.join(self.extracted_path, "smali*", *relative.split("/"))):
            with open(path, encoding="utf8") as f:
                if self.FLAG_RE.search(f.read()):
                    return True
        return False

    def deactivated_methods(self, class_data: str) -> list:
        return [
            body for body, flag_class in self.METHOD_RE.findall(class_data)
            if self.is_deactivated_flag(flag_class)
        ]

    def class_filter(self, class_data: str) -> bool:
        if 'Metadata key %s contains type other than boolean: %s' not in class_data:
            return False
        return len(self.deactivated_methods(class_data)) == 1

    def class_modifier(self, class_data, class_path) -> str:
        method_body = self.deactivated_methods(class_data)[0]
        return class_data.replace(method_body, self.METHOD_REPLACE)
