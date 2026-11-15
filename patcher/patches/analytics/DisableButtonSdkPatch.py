from ..Patch import Patch
import re


class DisableButtonSdkPatch(Patch):
    """
    Patch to never configure the Button SDK (affiliate attribution for taxi providers).
    On start it opens a session with device data and the Moovit user ID.
    Without configuration the SDK API is a no-op (e.g. purchasePath() returns NoOpPurchasePath).

    Removing the Button.configure() call.
    We are looking for the ButtonSdkInitializer class:
    .method public final create(Landroid/content/Context;)Ljava/lang/Object;
    from: com/moovit/app/taxi/providers/launch/ButtonSdkInitializer.smali
    """

    CONFIGURE_RE = re.compile(
        r"invoke-static\s+\{[\w\s,]*\},\s+Lcom/usebutton/sdk/Button;->configure\([\w/$;]*\)V\s*"
    )

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Button SDK patch..."

    def class_filter(self, class_data: str) -> bool:
        if re.search(r"^\.class\b.*\sLcom/usebutton/", class_data, re.MULTILINE):
            return False
        return len(self.CONFIGURE_RE.findall(class_data)) == 1

    def class_modifier(self, class_data, class_path) -> str:
        return self.CONFIGURE_RE.sub("", class_data)
