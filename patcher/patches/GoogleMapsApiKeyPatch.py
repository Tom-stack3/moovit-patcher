from .Patch import Patch
from .RPatch import RPatch
import hashlib
import os
import re


class GoogleMapsApiKeyPatch(Patch):
    """
    Keep the Maps web-service requests (Geocoding, Places Autocomplete,
    Geolocation) on Moovit's original API key instead of the user's key.

    Map tiles still need the user's key: they go through Play Services, which
    computes X-Android-Cert from the installed signing certificate (not
    settable from app code), so the original key is rejected there. The web
    services, though, are plain HTTP calls from Moovit's own client, which
    sets the key and the X-Android-* headers itself.

    So this patch rewrites that client to return the original key from its key
    getter and to send the original signing certificate as X-Android-Cert, both of which satisfy
    the key's restrictions. The user's key then only needs "Maps SDK for
    Android" enabled.
    """

    ORIGINAL_KEY = RPatch.MOOVIT_GOOGLE_API_KEY.decode()

    # The static String(Context) getter that reads the "google_wla_api_key"
    # resource. Matched by body, since R8 renames it.
    KEY_METHOD_RE = re.compile(
        r"\.method public static (\w+)\(Landroid/content/Context;\)Ljava/lang/String;"
        r"(?:(?!\.end method).)*?\"google_wla_api_key\".*?\.end method",
        re.DOTALL,
    )
    KEY_METHOD_STUB = (
        ".method public static {name}(Landroid/content/Context;)Ljava/lang/String;\n"
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
    # Saved by Extractor from the original APK Signing Block.
    PATH_TO_CERT = os.path.join("original", "signing-cert.der")

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Patching Google Maps web-service API key and signature..."
        self._original_signature = self._get_original_signature()

    def class_filter(self, class_data: str) -> bool:
        # The web-service client is the only class that both reads the Maps key
        # resource and sets the X-Android-Cert header on its requests.
        keywords = [
            "google_wla_api_key",
            "X-Android-Cert",
        ]
        return all(k in class_data for k in keywords) and bool(
            self.KEY_METHOD_RE.search(class_data)
        )

    def class_modifier(self, class_data, class_path) -> str:
        # Force the original key onto the web-service requests.
        class_data = self.KEY_METHOD_RE.sub(
            lambda m: self.KEY_METHOD_STUB.format(name=m.group(1), key=self.ORIGINAL_KEY),
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
        with open(cert_path, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()
