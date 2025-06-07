from .Patch import Patch
import re


class RemovePaymentSuggestionPatch(Patch):
    """
    Patch to remove "Join and Pay with Moovit" banner from app home screen.
    This "Pay with Moovit" feature is called MOT in the app.
    I once found the meaning of it, but forgot since then. Moovit O-something T-something.

    We are looking for the b0 class:
    .method public final a4(Lcom/google/firebase/perf/metrics/Trace;Lcom/moovit/payment/account/model/PaymentAccount;)V
    from: com/moovit/app/mot/b0.smali
    """

    LINE_RE = re.compile(
        r"""
        if-nez\s+v1,\s+:cond_1
        """,
        re.VERBOSE | re.DOTALL,
    )
    LINE_REPLACE = """
    if-eqz v1, :cond_1
    """

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
        line_body = self.LINE_RE.findall(class_data)[0]
        return class_data.replace(
            line_body,
            self.LINE_REPLACE,
        )
