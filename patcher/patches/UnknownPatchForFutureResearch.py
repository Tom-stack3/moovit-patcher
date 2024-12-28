from .Patch import Patch
import re


class UnknownPatchForFutureResearch(Patch):
    """
    Patch to unknown feature. Here if someone in the future will research it more.
    I tried understanding what is this function used for, but saw that it didn't have any 
    noticeable effect that was interesting to me.
    It might be interesting because it's very similar to the LiveLocationPatch (tv/a.java).
    It's the same function, but without the option to return FeatureFlag.ON.

    It returns FeautureFlag.SUBSCRIPTION, or FeatureFlag.OFF.
    Whether a feature should be paid for, or it's off.
    Didn't put the time to understand what features are used for it.
    Just patched it to return FeatureFlag.ON and FeatureFlag.OFF, and searched for an effect in the app,
    but didn't see any.

    The method we are looking for is:
    .method public e(Ljava/lang/String;)Lcom/moovit/app/feature/FeatureFlag;
    from: tv/b.java
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
        self.print_message = "[+] Patching Unknown feature on method..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            'com/moovit/app/feature/FeatureFlag',
            'Lcom/tranzmate/moovit/protocol/conf/MVFeatureFlag;->valueOf',
            'Lcom/moovit/app/feature/FeatureFlag;->SUBSCRIPTION:Lcom/moovit/app/feature/FeatureFlag;'
        ]
        non_keywords = [
            'Lcom/moovit/app/feature/FeatureFlag;->ON:Lcom/moovit/app/feature/FeatureFlag;'
        ]
        for k in keywords:
            if k not in class_data:
                return False
        for k in non_keywords:
            if k in class_data:
                return False
        return True

    def class_modifier(self, class_data) -> str:
        function_body = self.IS_FEATURE_ON_METHOD_RE.findall(class_data)[0]
        return class_data.replace(
            function_body,
            self.IS_FEATURE_ON_METHOD_REPLACE,
        )
