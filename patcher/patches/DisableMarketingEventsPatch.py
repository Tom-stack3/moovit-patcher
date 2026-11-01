from .Patch import Patch
import re


class DisableMarketingEventsPatch(Patch):
    """
    Patch to stop marketing events from being sent to AppsFlyer, Braze, Facebook and Firebase.

    Some of these events (e.g. "find_routes_tap", "suggested_routes_view") carry the trip
    origin and destination addresses.

    Making MarketingEventsManager.logEvent do nothing.
    We are looking for the MarketingEventsManager class:
    .method public h(Lw50/a;)V
    from: u50/g.smali
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+\w+\(L[\w/$]+;\)V\s*(
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
            'MarketingEventsManager',
            'logEvent: %s',
            'you must call initialize first',
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return True

    def class_modifier(self, class_data, class_path) -> str:
        method_body = self.METHOD_RE.findall(class_data)[0]
        return class_data.replace(
            method_body,
            self.METHOD_REPLACE,
        )
