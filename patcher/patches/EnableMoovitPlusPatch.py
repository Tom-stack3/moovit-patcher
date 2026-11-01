from .Patch import Patch
import re


class EnableMoovitPlusPatch(Patch):
    """
    Enable the Moovit+ subscription state locally.

    Moovit decides "is the user subscribed?" in SubscriptionBridgeImpl, which
    persists the purchased product ids ("subscribed_skus") and derives the
    subscription state from whether that set is non-empty:

        return !subscribedSkus.isEmpty();

    i.e. in smali:

        invoke-interface {vX}, Ljava/util/Collection;->isEmpty()Z
        move-result vY
        xor-int/lit8 vY, vY, 0x1

    The same expression feeds isSubscribed(), the initial value of the
    subscription StateFlow and its updates from the entitlements stream.
    Every premium package (ad free, AI search, safety, ...) and the Moovit+
    menu items read one of those, so forcing the result to true unlocks them
    and hides the "Upgrade to Moovit+" banners and popups.

    Matching is keyed off the unobfuscated "SubscriptionBridgeImpl" log tag
    and the isEmpty/xor shape, not the obfuscated class/method/field names
    that R8 reshuffles between releases.
    Up to 5.145 the gate was the "allow_subscription_features" dev config instead.
    """

    LOG_TAG = '"SubscriptionBridgeImpl"'

    NOT_EMPTY_RE = re.compile(
        r"(invoke-interface\s+\{\w+\},\s+Ljava/util/Collection;->isEmpty\(\)Z\s+"
        r"(?:\.line\s+\d+\s+)*"
        r"move-result\s+(\w+)\s+"
        r"(?:\.line\s+\d+\s+)*)"
        r"xor-int/lit8\s+\2,\s+\2,\s+0x1"
    )

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=True)
        self.print_message = "[+] Applying Enable Moovit+ patch..."

    def class_filter(self, class_data: str) -> bool:
        # SubscriptionBridgeImpl and its entitlements-observer lambda.
        return self.LOG_TAG in class_data and bool(self.NOT_EMPTY_RE.search(class_data))

    def class_modifier(self, class_data, class_path) -> str:
        return self.NOT_EMPTY_RE.sub(r"\g<1>const/16 \g<2>, 0x1", class_data)
