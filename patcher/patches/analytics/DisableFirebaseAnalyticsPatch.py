from ..Patch import Patch
import re


class DisableFirebaseAnalyticsPatch(Patch):
    """
    Patch to disable Firebase Analytics.

    - Stores "measurement_enabled" = false in the measurement preferences before the measurement
      client is created, the same value setAnalyticsCollectionEnabled(false) stores. This also stops
      the automatically collected events (first_open, session_start, screen_view...), whether the
      bundled or the Google Play services measurement module is used.
    - Makes logEvent, setUserId, setUserProperty and setCurrentScreen do nothing.

    We are looking for the measurement client class (zzff in the unobfuscated SDK):
    .method public static e(Landroid/content/Context;Landroid/os/Bundle;)Ldqn;
    from: dqn.smali
    And the FirebaseAnalytics class:
    .method public final b(Landroid/os/Bundle;Ljava/lang/String;)V
    .method public final c(Ljava/lang/String;Ljava/lang/String;)V
    .method public setCurrentScreen(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)V
    from: com/google/firebase/analytics/FirebaseAnalytics.smali
    """

    FIREBASE_ANALYTICS_CLASS = "Lcom/google/firebase/analytics/FirebaseAnalytics;"
    CLASS_RE = re.compile(r"^\.class\b.*\s(L[\w/$]+;)", re.MULTILINE)
    FACTORY_RE = r"\.method\s+public\s+static\s+\w+\(Landroid/content/Context;Landroid/os/Bundle;\){cls}\s*\.locals\s+\d+\s*"
    DISABLE_METHOD = "moovitPatcherDisableMeasurement"
    DISABLE_METHOD_SMALI = """
.method public static moovitPatcherDisableMeasurement(Landroid/content/Context;)V
    .locals 2

    const-string v0, "com.google.android.gms.measurement.prefs"
    const/4 v1, 0x0
    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v0
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    const-string v1, "measurement_enabled"
    const/4 p0, 0x0
    invoke-interface {v0, v1, p0}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V
    return-void
.end method
"""
    METHOD_RES = [
        # logEvent
        re.compile(r"\.method\s+public\s+final\s+\w+\((?:Ljava/lang/String;Landroid/os/Bundle;|Landroid/os/Bundle;Ljava/lang/String;)\)V\s*(.*?)\.end\s+method", re.DOTALL),
        # setUserId
        re.compile(r"\.method\s+public\s+final\s+\w+\(Ljava/lang/String;\)V\s*(.*?)\.end\s+method", re.DOTALL),
        # setUserProperty
        re.compile(r"\.method\s+public\s+final\s+\w+\(Ljava/lang/String;Ljava/lang/String;\)V\s*(.*?)\.end\s+method", re.DOTALL),
        re.compile(r"\.method\s+public\s+(?:final\s+)?setCurrentScreen\([\w/$;]*\)V\s*(.*?)\.end\s+method", re.DOTALL),
    ]
    METHOD_REPLACE = """
    .locals 0
    return-void
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=True)
        self.print_message = "[+] Applying Disable Firebase Analytics patch..."

    def class_name(self, class_data: str) -> str:
        match = self.CLASS_RE.search(class_data)
        return match.group(1) if match else ""

    def is_measurement_client(self, class_data: str) -> bool:
        if '"com.google.firebase.analytics.FirebaseAnalytics"' not in class_data:
            return False
        cls = re.escape(self.class_name(class_data))
        return re.search(self.FACTORY_RE.format(cls=cls), class_data) is not None

    def class_filter(self, class_data: str) -> bool:
        if self.class_name(class_data) == self.FIREBASE_ANALYTICS_CLASS:
            return True
        return self.is_measurement_client(class_data)

    def class_modifier(self, class_data, class_path) -> str:
        cls = self.class_name(class_data)
        if cls == self.FIREBASE_ANALYTICS_CLASS:
            # logEvent must exist, the others were removed by the optimizer in some versions.
            assert self.METHOD_RES[0].search(class_data), "logEvent not found"
            for method_re in self.METHOD_RES:
                for method_body in method_re.findall(class_data):
                    class_data = class_data.replace(method_body, self.METHOD_REPLACE)
            return class_data

        factory = re.search(self.FACTORY_RE.format(cls=re.escape(cls)), class_data)
        inject = f"""invoke-static {{p0}}, {cls}->{self.DISABLE_METHOD}(Landroid/content/Context;)V

    """
        return (
            class_data[:factory.end()] + inject + class_data[factory.end():]
            + self.DISABLE_METHOD_SMALI
        )
