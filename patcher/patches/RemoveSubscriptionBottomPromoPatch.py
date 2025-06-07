from .Patch import Patch
import re


class RemoveSubscriptionBottomPromoPatch(Patch):
    """
    Patch to remove "Join Moovit+ - Upgrade now" banner at the bottom of homescreen.

    Patching the Android lifecycle class that is responsible for rendering it.
    We are looking for the b class:
    .method public final b(Ljava/lang/Object;)V
    from: com/moovit/app/ads/promo/b.smali
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+final\s+[a-zA-Z]+\(Ljava/lang/Object;\)V\s*(
        .*?
        iget-object.*Lcom/moovit/app/ads/promo/MoovitSubscriptionsPromoCellFragment*
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
        self.print_message = "[+] Applying Remove Payment with Moovit Suggestion patch..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            'MoovitSubscriptionsPromoCellFragment',
            'Lcom/moovit/app/ads/promo',
            'Landroidx/lifecycle',
            'SyntheticClass',
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
