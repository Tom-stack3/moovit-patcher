from .Patch import Patch
import re


class DisableFirebasePerformancePatch(Patch):
    """
    Patch to deactivate Firebase Performance Monitoring.

    Changing the default of the "firebase_performance_collection_deactivated" flag to true.
    Deactivation wins over every other setting (manifest, shared preferences, remote config).
    We are looking for the ConfigurationConstants$CollectionDeactivated class:
    .method public d()Ljava/lang/Boolean;
    from: bj/b.smali
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+\w+\(\)Ljava/lang/Boolean;\s*
        \.locals\s+1\s*
        (?:\.line\s+\d+\s*)*
        (sget-object\s+v0,\s+Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;)
        \s*(?:\.line\s+\d+\s*)*
        return-object\s+v0\s*
        (?:\.line\s+\d+\s*)*
        \.end\s+method
        """,
        re.VERBOSE | re.DOTALL,
    )

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Firebase Performance patch..."

    def class_filter(self, class_data: str) -> bool:
        if not re.search(
            r'const-string\s+v0,\s+"firebase_performance_collection_deactivated"\s*(?:\.line\s+\d+\s*)*return-object\s+v0',
            class_data,
        ):
            return False
        return len(self.METHOD_RE.findall(class_data)) == 1

    def class_modifier(self, class_data, class_path) -> str:
        match = self.METHOD_RE.search(class_data)
        default = match.group(0)
        return class_data.replace(
            default,
            default.replace(match.group(1), match.group(1).replace("FALSE", "TRUE")),
        )
