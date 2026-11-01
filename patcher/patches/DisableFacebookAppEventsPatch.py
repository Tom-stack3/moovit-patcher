from .Patch import Patch
import re


class DisableFacebookAppEventsPatch(Patch):
    """
    Patch to stop the Facebook SDK from sending app events.
    Facebook login keeps working (the SDK still initializes).

    - Makes the "{app id}/activities" uploads do nothing: the app events batch request
      (returns null, as when the SDK is disabled) and the install ping.
    - Makes the AutoLogAppEventsEnabled and AdvertiserIDCollectionEnabled settings return false.

    We are looking for the classes:
    .method public static final i(...)Lcom/facebook/GraphRequest;
    from: com/facebook/appevents/k.smali (AppEventQueue)
    .method public final K(Landroid/content/Context;Ljava/lang/String;)V
    from: a8/u.smali (FacebookSdk)
    .method public static final b()Z / d()Z ...
    from: a8/l0.smali (UserSettingsManager)
    """

    ACTIVITIES_METHOD_RE = re.compile(
        r"""
        \.method\s+[\w\s-]*?\w+\([\w/$;\[]*\)(V|Lcom/facebook/GraphRequest;)\s*(
        (?:(?!\.end\s+method).)*?
        const-string\s+\w+,\s+"%s/activities"
        .*?
        )\.end\s+method
        """,
        re.VERBOSE | re.DOTALL,
    )
    ACTIVITIES_REPLACE = {
        "V": """
    .locals 0
    return-void
    """,
        "Lcom/facebook/GraphRequest;": """
    .locals 1
    const/4 v0, 0x0
    return-object v0
    """,
    }
    SETTING_KEYS = [
        "com.facebook.sdk.AutoLogAppEventsEnabled",
        "com.facebook.sdk.AdvertiserIDCollectionEnabled",
    ]
    # In <clinit>, each setting is created with its key and stored in a static field.
    SETTING_FIELD_RE = r'const-string\s+\w+,\s+"{key}"(?:(?!sput-object).)*?sput-object\s+\w+,\s+(L[\w/$]+;->\w+:L[\w/$]+;)'
    GETTER_RE = re.compile(
        r"\.method\s+public\s+static\s+final\s+\w+\(\)Z\s*(.*?)\.end\s+method", re.DOTALL
    )
    GETTER_REPLACE = """
    .locals 1
    const/4 v0, 0x0
    return v0
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=True)
        self.print_message = "[+] Applying Disable Facebook App Events patch..."

    def is_settings_class(self, class_data: str) -> bool:
        return all(k in class_data for k in self.SETTING_KEYS) and 'auto_event_setup_enabled' in class_data

    def class_filter(self, class_data: str) -> bool:
        if '"%s/activities"' in class_data and 'Lcom/facebook/' in class_data:
            return True
        return self.is_settings_class(class_data)

    def class_modifier(self, class_data, class_path) -> str:
        patched = class_data
        for return_type, method_body in self.ACTIVITIES_METHOD_RE.findall(class_data):
            patched = patched.replace(method_body, self.ACTIVITIES_REPLACE[return_type])

        if self.is_settings_class(class_data):
            fields = [
                re.search(self.SETTING_FIELD_RE.format(key=re.escape(k)), class_data, re.DOTALL).group(1)
                for k in self.SETTING_KEYS
            ]
            for method_body in self.GETTER_RE.findall(class_data):
                if any(f in method_body for f in fields):
                    patched = patched.replace(method_body, self.GETTER_REPLACE)

        assert patched != class_data, f"Nothing patched in {class_path}"
        return patched
