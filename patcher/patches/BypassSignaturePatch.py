from .Patch import Patch
import re
import subprocess

class BypassSignaturePatch(Patch):
    """
    Patch to bypass Android-Cert signature checks in different API requests.

    Replacing:
    ```smali
    .line 19
    const-string v1, "X-Android-Cert"

    .line 20
    # addRequestProperty is also used in the code
    invoke-virtual {p1, v1, v0}, Ljava/net/URLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V
    ```

    With:
    ```smali
    .line 19
    const-string v1, "X-Android-Cert"

    .line 20
    const-string v0, "<original signature of APK>"
    invoke-virtual {p1, v1, v0}, Ljava/net/URLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V
    ```
    """

    API_METHOD_RE = re.compile(
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
    PATH_TO_CERT = "extracted/original/META-INF/BNDLTOOL.RSA"

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=True)
        self.print_message = "[+] Patching Bypass Signature feature on method..."
        self._original_signature = self._get_original_signature()

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            'X-Android-Cert',
            'URLConnection',
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return True

    def class_modifier(self, class_data, class_path) -> str:
        print(f"Modifying class {class_path}")
        # entire_line_sequence: the entire sequence of lines that we found with the regex.
        # invoke_line: the line of the invoke-virtual method. We want to insert our patch right before it.
        # reg_name: the register name of the third parameter of the invoke-virtual method.
        # This is the register that we want to replace with the original signature.
        entire_line_sequence, invoke_line, reg_name = self.API_METHOD_RE.findall(class_data)[0]
        # print(f"Found sequence: {entire_line_sequence}")
        # print(f"Found invoke line: {invoke_line}")
        print(f"Found register name: {reg_name}")

        # Each class has a different register name and signature case.
        if "com/google/android/gms/internal/firebase-auth-api/zzacv.smali" in class_path:
            signature = self._original_signature.upper()
        elif "com/google/firebase/installations/remote/c.smali" in class_path:
            signature = self._original_signature.upper()
        elif "ConfigFetchHttpClient.smali" in class_path:
            signature = self._original_signature.upper()
        elif "com/google/firebase/remoteconfig/internal/d.smali" in class_path:
            signature = self._original_signature.upper()
        elif "ya0/a.smali" in class_path:
            signature = self._original_signature.lower()
        else:
            raise ValueError("Class path not found in switch case: " + class_path)

        move_string_to_reg = self.MOVE_STRING_TO_REG.format(reg_name, signature)
        new_invoke_line = move_string_to_reg + invoke_line

        return class_data.replace(
            entire_line_sequence,
            entire_line_sequence.replace(
                invoke_line,
                new_invoke_line
            )
        )

    def _get_original_signature(self) -> str:
        sig = subprocess.check_output(f"keytool -printcert -file {self.PATH_TO_CERT} | grep 'SHA1' | awk '{{print $NF}}'", shell=True).decode('utf-8').strip()
        return sig.replace(":", "").upper()
