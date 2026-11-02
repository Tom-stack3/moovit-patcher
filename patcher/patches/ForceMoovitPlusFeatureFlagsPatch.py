from .Patch import Patch
import re


class ForceMoovitPlusFeatureFlagsPatch(Patch):
    """
    Turn on the server feature flags behind the Moovit+ packages.

    Every Moovit+ package first checks a configuration flag sent by Moovit's
    servers per metro, and only then the subscription:

        if (config.get(IS_AI_SEARCH_FEATURE_SUPPORTED) != SUBSCRIPTION) return INACTIVE;
        return isSubscribed() ? ACTIVE : OFFER;

    So a package the server turned off stays hidden even with Moovit+ enabled.

    All configuration keys are parsed from their raw string value by one
    method, which logs "Missing configuration key: " when the key is absent:

        String value = (String) map.get(this.key);

    This patch overrides that string for the Moovit+ feature keys before it is
    parsed, so every reader of the flag sees it on. Feature flags are forced to
    "SUBSCRIPTION" (with "ON" the packages treat the feature as not part of
    Moovit+ and hide it), boolean flags to "1".

    TOM_PRESENTATION_TYPE is left alone: it picks either Live Location or
    Trip on Map, never both.
    """

    FORCED_VALUES = {
        "IS_AI_SEARCH_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_COMPARE_ON_MAP_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_DEFAULT_TAB_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_RT_NOTIFICATIONS_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_SAFE_RIDE_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_SHARE_RIDE_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_TRAFFIC_LAYER_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_TRIP_PLAN_SORT_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_ADVANCED_TP_ROUTES_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_TRIP_INSIGHTS_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_TRIP_PLAN_ADVANCED_TIME_PICKER_SUPPORTED": "SUBSCRIPTION",
        "IS_MOVE_IT_AROUND_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_TOM_FEATURE_SUPPORTED": "SUBSCRIPTION",
        "IS_GREEN_RIDE_PACKAGE_SUPPORTED": "1",
    }

    # The raw value lookup in the configuration key's a(Map) method.
    LOOKUP_RE = re.compile(
        r"(\.method public final a\(Ljava/util/Map;\)Ljava/lang/Object;\s+"
        r"\.locals )(\d+)(\s+"
        r"(?:\.line\s+\d+\s+)*"
        r"iget-object (\w+), p0, L[\w/$]+;->\w+:Ljava/lang/String;\s+"
        r"(?:\.line\s+\d+\s+)*"
        r"invoke-interface \{(\w+), \4\}, Ljava/util/Map;->get\(Ljava/lang/Object;\)Ljava/lang/Object;\s+"
        r"(?:\.line\s+\d+\s+)*"
        r"move-result-object \5\s+"
        r"(?:\.line\s+\d+\s+)*"
        r"check-cast \5, Ljava/lang/String;\n)"
    )

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Force Moovit+ feature flags patch..."

    def class_filter(self, class_data: str) -> bool:
        return '"Missing configuration key: "' in class_data and bool(self.LOOKUP_RE.search(class_data))

    def class_modifier(self, class_data, class_path) -> str:
        def inject(m):
            locals_count = int(m.group(2))
            tmp, key, value = f"v{locals_count}", m.group(4), m.group(5)
            overrides = []
            for i, (flag, forced) in enumerate(self.FORCED_VALUES.items()):
                overrides.append(
                    f'    const-string {tmp}, "{flag}"\n'
                    f"    invoke-virtual {{{tmp}, {key}}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z\n"
                    f"    move-result {tmp}\n"
                    f"    if-eqz {tmp}, :force_flag_{i}\n"
                    f'    const-string {value}, "{forced}"\n'
                    f"    :force_flag_{i}\n"
                )
            return m.group(1) + str(locals_count + 1) + m.group(3) + "\n" + "".join(overrides)

        return self.LOOKUP_RE.sub(inject, class_data, count=1)
