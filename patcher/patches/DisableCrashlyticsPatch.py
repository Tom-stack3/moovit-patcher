from .Patch import Patch
import re


class DisableCrashlyticsPatch(Patch):
    """
    Patch to disable Firebase Crashlytics data collection (crash reports, session events).
    Reports are kept on the device and never sent.

    Making DataCollectionArbiter.isAutomaticDataCollectionEnabled() return false.
    We are looking for the DataCollectionArbiter class:
    .method public declared-synchronized d()Z
    from: yh/w.smali
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
            'firebase_crashlytics_collection_enabled',
            'An invalid data collection token was used.',
            'Could not read data collection permission from manifest',
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
