from ..Patch import Patch
import re


class DisableBrazePatch(Patch):
    """
    Patch to disable the Braze SDK: no sessions, device data, user attributes or location
    (location collection is enabled in the app's Braze config).
    Braze in-app messages, content cards and Braze push notifications stop as well.

    Making Braze.isDisabled() return true, the same as Braze.disableSdk() does.
    We are looking for the Braze$Companion class:
    .method public final isDisabled()Z
    from: com/braze/Braze$Companion.smali
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+final\s+isDisabled\(\)Z\s*(
        .*?
        )\.end\s+method
        """,
        re.VERBOSE | re.DOTALL,
    )
    METHOD_REPLACE = """
    .locals 1
    const/4 v0, 0x1
    return v0
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Braze patch..."

    def class_filter(self, class_data: str) -> bool:
        if not re.search(r"^\.class\b.*\sLcom/braze/Braze\$Companion;", class_data, re.MULTILINE):
            return False
        return bool(self.METHOD_RE.search(class_data))

    def class_modifier(self, class_data, class_path) -> str:
        method_body = self.METHOD_RE.findall(class_data)[0]
        return class_data.replace(
            method_body,
            self.METHOD_REPLACE,
        )
