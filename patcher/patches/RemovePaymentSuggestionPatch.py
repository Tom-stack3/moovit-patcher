from .Patch import Patch
import re


class RemovePaymentSuggestionPatch(Patch):
    """
    Patch to remove "Join and Pay with Moovit" banner from app home screen.
    This "Pay with Moovit" feature is called MOT in the app.
    I once found the meaning of it, but forgot since then. Moovit O-something T-something.

    We are looking for the MOT home section fragment, which logs
    "MOT is not enabled!" and hides itself when MOT is not supported.
    """

    # The MOT_SUPPORT_VALIDATOR check right before the "not enabled" log:
    #     if (!TRUE.equals(motSupported)) { log("MOT is not enabled!"); hideSection(); }
    # Dropping the branch makes the section always take the hide path.
    BRANCH_RE = re.compile(
        r"""
        if-nez\s+\w+,\s+:cond_\w+\s+
        (?=(?:\.line\s+\d+\s+)*const-string\s+\w+,\s+"MOT\ is\ not\ enabled!")
        """,
        re.VERBOSE,
    )

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Remove Payment with Moovit Suggestion patch..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            'MotSection',
            'MOT is not enabled!',
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return True

    def class_modifier(self, class_data, class_path) -> str:
        if not self.BRANCH_RE.search(class_data):
            raise ValueError("MOT support check not found in " + class_path)
        return self.BRANCH_RE.sub("", class_data, count=1)
