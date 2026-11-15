from ..Patch import Patch
import re


class DisableRevenueCatAttributionPatch(Patch):
    """
    Patch to stop reporting device identifiers and attribution IDs to RevenueCat.
    RevenueCat itself (subscriptions) keeps working.

    On start, the app calls collectDeviceIdentifiers() (advertising ID, Android ID, IP address)
    and sends the attribution provider ID as RevenueCat subscriber attributes.

    Making RevenueCatAttributionSynchronizer.start() do nothing.
    We are looking for the RevenueCatAttributionSynchronizer class:
    .method public final b()V
    from: com/moovit/lib/revenuecat/attribution/a.smali
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+final\s+\w+\(\)V\s*(
        (?:(?!\.end\s+method).)*?
        const-string\s+\w+,\s+"start:\slaunched;\sawaiting\sSDK\sconfiguration\."
        .*?
        )\.end\s+method
        """,
        re.VERBOSE | re.DOTALL,
    )
    METHOD_REPLACE = """
    .locals 0
    return-void
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable RevenueCat Attribution patch..."

    def class_filter(self, class_data: str) -> bool:
        if '"RevenueCatAttributionSynchronizer"' not in class_data:
            return False
        return len(self.METHOD_RE.findall(class_data)) == 1

    def class_modifier(self, class_data, class_path) -> str:
        method_body = self.METHOD_RE.findall(class_data)[0]
        return class_data.replace(method_body, self.METHOD_REPLACE)
