from .Patch import Patch
import re


class RemoveTaxiTripResultsPatch(Patch):
    """
    Patch to remove the taxi (e.g. Gett) option from the trip plan results.

    The taxi suggestions are planned by Moovit's server, which skips them when
    the trip plan request has skipTaxiSearch set. Every request builder marks
    the field as set, so we only force its value to true where the Thrift
    serializer writes it:

        sget-object vF, MVTripPlanRequest;->SKIP_TAXI_SEARCH_FIELD_DESC
        invoke-virtual {vProtocol, vF}, L...;->writeFieldBegin(TField)V
        iget-boolean vX, vReq, MVTripPlanRequest;->skipTaxiSearch:Z
        invoke-virtual {vProtocol, vX}, L...;->writeBool(Z)V

    (hashCode() also reads the field into a (Z)V call, hence the field header.)

    Covers trip results only; the home screen taxi sections need
    DisableTaxiProvidersPatch.
    """

    WRITE_RE = re.compile(
        r"(sget-object (\w+), Lcom/tranzmate/moovit/protocol/tripplanner/MVTripPlanRequest;->\w+:L[\w/$]+;\s+"
        r"(?:\.line\s+\d+\s+)*"
        r"invoke-virtual \{(\w+), \2\}, L[\w/$]+;->\w+\(L[\w/$]+;\)V\s+"
        r"(?:\.line\s+\d+\s+)*)"
        r"iget-boolean (\w+), \w+, Lcom/tranzmate/moovit/protocol/tripplanner/MVTripPlanRequest;->skipTaxiSearch:Z"
        r"(\s+(?:\.line\s+\d+\s+)*invoke-virtual \{\3, \4\}, L[\w/$]+;->\w+\(Z\)V)"
    )

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Remove taxi trip results patch..."

    def class_filter(self, class_data: str) -> bool:
        return "MVTripPlanRequest;->skipTaxiSearch:Z" in class_data and bool(self.WRITE_RE.search(class_data))

    def class_modifier(self, class_data, class_path) -> str:
        return self.WRITE_RE.sub(r"\g<1>const/4 \g<4>, 0x1\g<5>", class_data, count=1)
