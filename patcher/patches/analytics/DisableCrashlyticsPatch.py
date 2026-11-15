from ..Patch import Patch
import re


class DisableCrashlyticsPatch(Patch):
    """
    Patch to disable Firebase Crashlytics data collection (crash reports, session events).
    Reports are kept on the device and never sent.

    Making DataCollectionArbiter.isAutomaticDataCollectionEnabled() return false.
    Firebase Sessions also checks it before sending session events.
    We are looking for the DataCollectionArbiter class (merged with unrelated classes):
    .method public declared-synchronized u()Z
    from: x93.smali
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+declared-synchronized\s+\w+\(\)Z\s*(
        .*?
        )\.end\s+method
        """,
        re.VERBOSE | re.DOTALL,
    )
    METHOD_REPLACE = """
    .locals 1
    const/4 v0, 0x0
    return v0
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Crashlytics patch..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            '"firebase_crashlytics_collection_enabled"',
            '"com.google.firebase.crashlytics"',
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return len(self.METHOD_RE.findall(class_data)) == 1

    def class_modifier(self, class_data, class_path) -> str:
        method_body = self.METHOD_RE.findall(class_data)[0]
        return class_data.replace(
            method_body,
            self.METHOD_REPLACE,
        )
