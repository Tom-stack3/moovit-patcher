from .Patch import Patch
import re


class DisableAdsPatch(Patch):
    """
    Patch to disable ads in the app.

    We are looking for the MobileAdsManafer class
    .method public U()Z
    from: lu/k0.java
    """

    """
    .method public [a-zA-Z]()Z
    *
    const-string v1, "is_ads_free_version"
    *
    .end method
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+[a-zA-Z]+\(\)Z\s*(
        .*?
        const-string\s+\w+,\s+"is_ads_free_version"\s*
        .*?
        )\.end\s+method
        """,
        re.VERBOSE | re.DOTALL,
    )
    # Create a method that returns true always
    METHOD_REPLACE = """
    .locals 1
    const/4 v0, 0x1
    return v0
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Ads patch..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            'is_ads_free_version',
            'ads_rewarded_ad_load_initiators',
            'MobileAdsManager'
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return True

    def class_modifier(self, class_data, class_path) -> str:
        function_body = self.METHOD_RE.findall(class_data)[0]
        print(function_body)
        print("REPLACE")
        print(self.METHOD_REPLACE)
        # return class_data
        return class_data.replace(
            function_body,
            self.METHOD_REPLACE,
        )
