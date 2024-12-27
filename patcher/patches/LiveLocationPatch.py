from .Patch import Patch
import re


class LiveLocationPatch(Patch):
    """
    Patch to enable Live Location feature of buses.

    The method we are looking for is:
    .method public e(Ljava/lang/String;)Lcom/moovit/app/feature/FeatureFlag;
    from: tv/a.java
    """

    IS_FEATURE_ON_METHOD_RE = re.compile(
        "\.method public [a-zA-Z]+\(Ljava/lang/String;\)Lcom/moovit/app/feature/FeatureFlag;\s*(.*?)\.end method",
        re.DOTALL,
    )
    IS_FEATURE_ON_METHOD_REPLACE = """
    .locals 1
    sget-object p1, Lcom/moovit/app/feature/FeatureFlag;->ON:Lcom/moovit/app/feature/FeatureFlag;
    return-object p1
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path)
        self.print_message = "[+] Patching Live Location feature on method..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            'com/moovit/app/feature/FeatureFlag',
            'Lcom/tranzmate/moovit/protocol/conf/MVFeatureFlag;->valueOf',
            'Lcom/moovit/app/feature/FeatureFlag;->ON:Lcom/moovit/app/feature/FeatureFlag;'
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return True

    def class_modifier(self, class_data) -> str:
        function_body = self.IS_FEATURE_ON_METHOD_RE.findall(class_data)[0]
        return class_data.replace(
            function_body,
            self.IS_FEATURE_ON_METHOD_REPLACE,
        )
