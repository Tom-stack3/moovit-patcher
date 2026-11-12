from ..Patch import Patch
import re


class DisableMarketingEventsPatch(Patch):
    """
    Patch to stop marketing events from being sent to AppsFlyer and Braze.

    Some of these events (e.g. "find_routes_tap", "suggested_routes_view") carry the trip
    origin and destination addresses.

    Making DefaultAnalyticsMarketingManager.logEvent do nothing.
    We are looking for the DefaultAnalyticsMarketingManager class:
    .method public final a(Lokb;)V
    from: sy4.smali
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+(?:final\s+)?\w+\(L[\w/$]+;\)V\s*(
        .*?
        const-string\s+\w+,\s+"logEvent:\s%s"\s*
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
        self.print_message = "[+] Applying Disable Marketing Events patch..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            '"DefaultAnalyticsMarketingManager"',
            '"logEvent: %s"',
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
