from .Patch import Patch
from .RPatch import RPatch
import os
import re
import shutil
import subprocess


def _find_keytool() -> str:
    """
    Locate the keytool executable even when it is not on PATH.

    The patcher already depends on a JDK (apktool is run via ``java``), so
    derive keytool from the running JRE's ``java.home`` as a fallback.
    """
    found = shutil.which("keytool")
    if found:
        return found
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidate = os.path.join(java_home, "bin", "keytool")
        if os.path.exists(candidate) or os.path.exists(candidate + ".exe"):
            return candidate
    try:
        out = subprocess.check_output(
            ["java", "-XshowSettings:properties", "-version"],
            stderr=subprocess.STDOUT,
        ).decode("utf-8", "replace")
    except (OSError, subprocess.CalledProcessError):
        return "keytool"
    for line in out.splitlines():
        if "java.home" in line:
            home = line.split("=", 1)[-1].strip()
            candidate = os.path.join(home, "bin", "keytool")
            if os.path.exists(candidate) or os.path.exists(candidate + ".exe"):
                return candidate
    return "keytool"


class GoogleMapsApiKeyPatch(Patch):
    """
    Keep the Maps web-service requests (Geocoding, Places Autocomplete,
    Geolocation) on Moovit's original API key instead of the user's key.

    Map tiles still need the user's key: they go through Play Services, which
    computes X-Android-Cert from the installed signing certificate (not
    settable from app code), so the original key is rejected there. The web
    services, though, are plain HTTP calls from Moovit's own client ya0/a.smali,
    which sets the key and the X-Android-* headers itself.

    So this patch rewrites ya0/a.smali to return the original key from P0 and to send
    the original signing certificate as X-Android-Cert, both of which satisfy
    the key's restrictions. The user's key then only needs "Maps SDK for
    Android" enabled.
    """

    ORIGINAL_KEY = RPatch.MOOVIT_GOOGLE_API_KEY.decode()

    P0_METHOD_RE = re.compile(
        r"\.method public static P0\(Landroid/content/Context;\)Ljava/lang/String;.*?\.end method",
        re.DOTALL,
    )
    P0_STUB = (
        ".method public static P0(Landroid/content/Context;)Ljava/lang/String;\n"
        "    .locals 1\n\n"
        '    const-string v0, "{key}"\n\n'
        "    return-object v0\n"
        ".end method"
    )

    CERT_RE = re.compile(
        r"""(
        const-string\s+\w+,\s+"X-Android-Cert"\s*
        .*?  # Match any number of lines between the two lines
        (\s*invoke-virtual\s+\{\w+,\s+\w+,\s+(\w+)\},\s+Ljava/net/URLConnection;->(?:set|add)RequestProperty\(Ljava/lang/String;Ljava/lang/String;\)V)
        )
        """,
        re.VERBOSE | re.DOTALL,
    )
    MOVE_STRING_TO_REG = """
    const-string {}, "{}"
    """
    PATH_TO_CERT = os.path.join("original", "META-INF", "BNDLTOOL.RSA")

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Patching Google Maps web-service API key and signature..."
        self._original_signature = self._get_original_signature()

    def class_filter(self, class_data: str) -> bool:
        # ya0/a is the only class that both reads the Maps key resource and
        # sets the X-Android-Cert header on its web-service requests.
        keywords = [
            "google_wla_api_key",
            "X-Android-Cert",
            "P0(Landroid/content/Context;)Ljava/lang/String;",
        ]
        return all(k in class_data for k in keywords)

    def class_modifier(self, class_data, class_path) -> str:
        # Force the original key onto the web-service requests.
        class_data = self.P0_METHOD_RE.sub(
            self.P0_STUB.format(key=self.ORIGINAL_KEY),
            class_data,
            count=1,
        )

        # Force the original signature onto the X-Android-Cert header.
        entire_line_sequence, invoke_line, reg_name = self.CERT_RE.findall(class_data)[0]
        move_string_to_reg = self.MOVE_STRING_TO_REG.format(
            reg_name, self._original_signature.lower()
        )
        new_invoke_line = move_string_to_reg + invoke_line
        return class_data.replace(
            entire_line_sequence,
            entire_line_sequence.replace(invoke_line, new_invoke_line),
        )

    def _get_original_signature(self) -> str:
        cert_path = os.path.join(self.extracted_path, self.PATH_TO_CERT)
        out = subprocess.check_output(
            [_find_keytool(), "-printcert", "-file", cert_path]
        ).decode("utf-8")
        for line in out.splitlines():
            if "SHA1" in line:
                sig = line.split()[-1]
                return sig.replace(":", "")
        raise ValueError("SHA1 signature not found in certificate")
