from .Patch import Patch
import re


class EnableMoovitPlusPatch(Patch):
    """
    Enable the Moovit+ subscription state locally.

    Moovit gates every "is the user subscribed?" decision on a single developer
    config, "allow_subscription_features" (AppDevConfigs). Both
    SubscriptionManager.isSubscribed and the MoovitSubscriptionsManager state
    resolver return "subscribed" as soon as it is on, which in turn hides the
    "Upgrade to Moovit+" banners and popups. The config is declared as:

        new h.a("allow_subscription_features", false)

    i.e. in smali, inside the defining class' static initializer:

        const-string vX, "allow_subscription_features"
        const/4 vY, 0x0                                         # default: false
        invoke-direct {.., vX, vY}, L..$a;-><init>(Ljava/lang/String;Z)V

    Flipping that default from 0x0 to 0x1 is deliberately version-resilient: it
    keys off the unobfuscated config name and the boolean-config constructor
    shape, not the obfuscated class/method/field names (g0, a0$d, h, a, qv.a)
    that R8 reshuffles between releases.
    """

    CONFIG_NAME = "allow_subscription_features"

    # From the const-string that loads the config name, through the boolean
    # default it is constructed with, up to the h.a(String, boolean) ctor call.
    # Non-greedy so the captured "0x0" is the default bound to THIS config, and
    # the trailing ctor match guards against flipping an unrelated const.
    DEFAULT_RE = re.compile(
        r'(const-string\s+\w+,\s+"' + re.escape(CONFIG_NAME) + r'"'
        r'(?:(?!const-string).)*?'
        r'const/4\s+\w+,\s+)0x0'
        r'((?:(?!const-string).)*?'
        r'invoke-direct\s+\{[^}]*\},\s+L[\w/$]+;-><init>\(Ljava/lang/String;Z\)V)',
        re.DOTALL,
    )

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Enable Moovit+ patch..."

    def class_filter(self, class_data: str) -> bool:
        return (
            '"' + self.CONFIG_NAME + '"' in class_data
            and self.DEFAULT_RE.search(class_data) is not None
        )

    def class_modifier(self, class_data, class_path) -> str:
        return self.DEFAULT_RE.sub(r"\g<1>0x1\g<2>", class_data, count=1)
