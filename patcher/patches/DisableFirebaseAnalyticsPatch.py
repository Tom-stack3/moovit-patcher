from .Patch import Patch
import re


class DisableFirebaseAnalyticsPatch(Patch):
    """
    Patch to disable Firebase Analytics.

    - Calls setMeasurementEnabled(false) when FirebaseAnalytics is created, which also stops
      the automatically collected events (first_open, session_start, screen_view...).
      The setting is persisted, so it applies from the next launch on, before any instance exists.
    - Makes logEvent, setUserId, setUserProperty and setCurrentScreen do nothing.

    We are looking for the FirebaseAnalytics class:
    .method public constructor <init>(Lcom/google/android/gms/internal/measurement/zzdf;)V
    .method public final a(Ljava/lang/String;Landroid/os/Bundle;)V
    .method public final b(Ljava/lang/String;)V
    .method public final c(Ljava/lang/String;Ljava/lang/String;)V
    .method public final setCurrentScreen(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)V
    from: com/google/firebase/analytics/FirebaseAnalytics.smali
    """

    # zzdf.zza(Boolean) is setMeasurementEnabled in the bundled play-services-measurement.
    CONSTRUCTOR_RE = re.compile(
        r"""
        \.method\s+public\s+constructor\s+<init>\(Lcom/google/android/gms/internal/measurement/zzdf;\)V\s*
        \.locals\s+0\s*(
        .*?
        )return-void\s*(?:\.line\s+\d+\s*)*\.end\s+method
        """,
        re.VERBOSE | re.DOTALL,
    )
    CONSTRUCTOR_INJECT = """
    sget-object v0, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;
    invoke-virtual {p1, v0}, Lcom/google/android/gms/internal/measurement/zzdf;->zza(Ljava/lang/Boolean;)V
    """
    METHOD_RES = [
        # logEvent
        re.compile(r"\.method\s+public\s+final\s+\w+\(Ljava/lang/String;Landroid/os/Bundle;\)V\s*(.*?)\.end\s+method", re.DOTALL),
        # setUserId
        re.compile(r"\.method\s+public\s+final\s+\w+\(Ljava/lang/String;\)V\s*(.*?)\.end\s+method", re.DOTALL),
        # setUserProperty
        re.compile(r"\.method\s+public\s+final\s+\w+\(Ljava/lang/String;Ljava/lang/String;\)V\s*(.*?)\.end\s+method", re.DOTALL),
        re.compile(r"\.method\s+public\s+final\s+setCurrentScreen\([\w/$;]*\)V\s*(.*?)\.end\s+method", re.DOTALL),
    ]
    METHOD_REPLACE = """
    .locals 0
    return-void
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Firebase Analytics patch..."

    def class_filter(self, class_data: str) -> bool:
        if not re.search(
            r"^\.class\b.*\sLcom/google/firebase/analytics/FirebaseAnalytics;",
            class_data,
            re.MULTILINE,
        ):
            return False
        return 'Lcom/google/android/gms/internal/measurement/zzdf;' in class_data

    def class_modifier(self, class_data, class_path) -> str:
        constructor = self.CONSTRUCTOR_RE.search(class_data)
        body = constructor.group(1)
        class_data = (
            class_data[:constructor.start()]
            + constructor.group(0)
            .replace(".locals 0", ".locals 1", 1)
            .replace(body, body + self.CONSTRUCTOR_INJECT, 1)
            + class_data[constructor.end():]
        )
        for method_re in self.METHOD_RES:
            method_body = method_re.findall(class_data)[0]
            class_data = class_data.replace(method_body, self.METHOD_REPLACE)
        return class_data
