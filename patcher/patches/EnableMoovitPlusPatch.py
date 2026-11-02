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
    menu items read one of those.

    Other screens (the "Remove ads with Moovit+" promo cell, live location
    paywalls) skip the bridge and ask IsSubscribedStreamUseCase and its
    one-shot sibling instead. They apply the same !isEmpty() to the
    entitlements list, compiled as "xor-int/2addr vY, vOne". The Moovit+ tab
    (MyMoovitSubscriptionViewModel) does the same on the owned subscriptions
    list to choose between the "Go premium" and the subscriber page. Forcing
    all of them to true unlocks the features and hides the upgrade banners
    and popups.

    Matching is keyed off unobfuscated names (the "SubscriptionBridgeImpl" log
    tag, the entitlements repository, IsSubscribedStreamUseCase,
    MyMoovitSubscriptionViewModel) and the
    isEmpty/xor shape, not the obfuscated class/method/field names that R8
    reshuffles between releases.
    """

    ANCHORS = (
        '"SubscriptionBridgeImpl"',
        "Lcom/moovit/lib/subscription/entitlements/a;",
        "IsSubscribedStreamUseCase",
        "MyMoovitSubscriptionViewModel",
    )

    NOT_EMPTY_RE = re.compile(
        r"(invoke-interface(?:/range)?\s+\{\w+(?:\s+\.\.\s+\w+)?\},\s+Ljava/util/Collection;->isEmpty\(\)Z\s+"
        r"(?:\.line\s+\d+\s+)*"
        r"move-result\s+(\w+)\s+"
        r"(?:\.line\s+\d+\s+)*)"
        r"xor-int/(?:lit8\s+\2,\s+\2,\s+0x1|2addr\s+\2,\s+\w+)"
    )

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=True)
        self.print_message = "[+] Applying Enable Moovit+ patch..."

    def class_filter(self, class_data: str) -> bool:
        # SubscriptionBridgeImpl, its entitlements-observer lambda and the
        # IsSubscribedStreamUseCase entitlement checks and the Moovit+ tab.
        return any(a in class_data for a in self.ANCHORS) and bool(self.NOT_EMPTY_RE.search(class_data))

    def class_modifier(self, class_data, class_path) -> str:
        return self.NOT_EMPTY_RE.sub(r"\g<1>const/16 \g<2>, 0x1", class_data)
