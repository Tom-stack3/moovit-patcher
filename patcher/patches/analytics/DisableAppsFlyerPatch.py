from ..Patch import Patch
import re


class DisableAppsFlyerPatch(Patch):
    """
    Patch to never initialize or start the AppsFlyer SDK (install attribution, sessions, ad IDs).
    AppsFlyer deep links (OneLink) will not resolve anymore.

    Making the methods that call AppsFlyerLib.init() and AppsFlyerLib.start() do nothing.
    We are looking for the AppsFlyerManager class:
    .method public final b()V
    .method public final e(Landroid/content/ContextWrapper;)V
    from: dr0.smali
    """

    METHOD_RES = [
        re.compile(
            r"""
            \.method\s+public\s+final\s+\w+\([\w/$;]*\)V\s*(
            (?:(?!\.end\s+method).)*?
            ->init\(Ljava/lang/String;Lcom/appsflyer/AppsFlyerConversionListener;Landroid/content/Context;\)
            .*?
            )\.end\s+method
            """,
            re.VERBOSE | re.DOTALL,
        ),
        re.compile(
            r"""
            \.method\s+public\s+final\s+\w+\(L[\w/$]+;\)V\s*(
            (?:(?!\.end\s+method).)*?
            Lcom/appsflyer/AppsFlyerLib;->start\(Landroid/content/Context;\)V
            .*?
            )\.end\s+method
            """,
            re.VERBOSE | re.DOTALL,
        ),
    ]
    METHOD_REPLACE = """
    .locals 0
    return-void
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable AppsFlyer patch..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            'AppsFlyerManager',
            'Start tracking called.',
            'Lcom/appsflyer/deeplink/DeepLinkListener;',
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return True

    def class_modifier(self, class_data, class_path) -> str:
        for method_re in self.METHOD_RES:
            method_body = method_re.findall(class_data)[0]
            class_data = class_data.replace(
                method_body,
                self.METHOD_REPLACE,
            )
        return class_data
