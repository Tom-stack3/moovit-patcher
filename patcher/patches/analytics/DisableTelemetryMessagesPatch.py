from ..Patch import Patch
import glob
import os
import re


class DisableTelemetryMessagesPatch(Patch):
    """
    Patch to stop device telemetry messages sent over the Kinesis "ServerStream".

    Dropped messages (by the type of the MVServerMessage union value):
    - MVStaticMetricsServerMessage: device model, build, CPU, RAM, storage, sensors, display.
    - MVDynamicMetricsServerMessage: OS, timezone, memory, networks, carrier, battery, app permissions.
    - MVSetAdvertisingInfoRequest: AppsFlyer ID, App Set ID, limit ad tracking flag.
    - MVInstallationAttribution: install referrer, click and install time, deep link, carrier.
    - MVApplicationInfos: list of installed applications (unused, dropped just in case).

    A dropped message is replaced with null, which the app already treats as "nothing to write",
    and a record that writes no bytes is not saved by KinesisStreamRecorder.
    We are looking for the ThriftKinesisable classes (a sync and a suspend variant):
    .method public final a(Ljava/io/OutputStream;Lgz3;)Ljava/lang/Object;
    from: m8j.smali and com/moovit/core/aws/kinesis/g.smali
    """

    WRITE_METHOD_RE = re.compile(
        r"\.method\s+public\s+final\s+\w+\(Ljava/io/OutputStream;L[\w/$]+;\)Ljava/lang/Object;.*?\.end\s+method",
        re.DOTALL,
    )
    TBASE_WRITE_RE = re.compile(r"invoke-interface\s+\{(\w+),\s+\w+\},\s+Lorg/apache/thrift/TBase;->\w+\(L[\w/$]+;\)V")
    NULL_CHECK_RE = r"if-nez\s+{tbase},\s+:\w+"
    UNION_GETTER_RE = re.compile(
        r"\.method\s+public\s+final\s+(\w+)\(\)Ljava/lang/Object;\s*\.locals\s+0\s*(?:\.line\s+\d+\s*)*"
        r"iget-object\s+p0,\s+p0,\s+Lorg/apache/thrift/TUnion;->value_:Ljava/lang/Object;"
    )
    FILTER_METHOD = "moovitPatcherDropTelemetry"
    DROPPED_TYPES = [
        "Lcom/tranzmate/moovit/protocol/metrics/MVStaticMetricsServerMessage;",
        "Lcom/tranzmate/moovit/protocol/metrics/MVDynamicMetricsServerMessage;",
        "Lcom/tranzmate/moovit/protocol/users/MVSetAdvertisingInfoRequest;",
        "Lcom/tranzmate/moovit/protocol/kinesis/MVInstallationAttribution;",
        "Lcom/tranzmate/moovit/protocol/datacollection/MVApplicationInfos;",
    ]

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=True)
        self.print_message = "[+] Applying Disable Telemetry Messages patch..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            'ThriftKinesisable',
            'failed to write thrift kinesisable as bytes',
            'Lorg/apache/thrift/TBase;',
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return self.WRITE_METHOD_RE.search(class_data) is not None

    def union_getter(self) -> str:
        path = glob.glob(os.path.join(self.extracted_path, "smali*", "org", "apache", "thrift", "TUnion.smali"))[0]
        with open(path, encoding="utf8") as f:
            return self.UNION_GETTER_RE.search(f.read()).group(1)

    def filter_method(self, class_name: str) -> str:
        checks = "".join(
            f"""
    instance-of v1, v0, {t}
    if-nez v1, :drop
""" for t in self.DROPPED_TYPES
        )
        return f"""
.method public static {self.FILTER_METHOD}(Lorg/apache/thrift/TBase;)Lorg/apache/thrift/TBase;
    .locals 2

    instance-of v0, p0, Lcom/tranzmate/moovit/protocol/kinesis/MVServerMessage;
    if-eqz v0, :keep
    move-object v0, p0
    check-cast v0, Lorg/apache/thrift/TUnion;
    invoke-virtual {{v0}}, Lorg/apache/thrift/TUnion;->{self.union_getter()}()Ljava/lang/Object;
    move-result-object v0
{checks}
    :keep
    return-object p0

    :drop
    const/4 v0, 0x0
    return-object v0
.end method
"""

    def class_modifier(self, class_data, class_path) -> str:
        class_name = re.search(r"^\.class\b.*\s(L[\w/$]+;)", class_data, re.MULTILINE).group(1)
        method = self.WRITE_METHOD_RE.search(class_data).group(0)
        tbase = self.TBASE_WRITE_RE.search(method).group(1)
        # The null check guarding the write, the last one on that register before it.
        write_pos = self.TBASE_WRITE_RE.search(method).start()
        null_check = list(re.finditer(self.NULL_CHECK_RE.format(tbase=tbase), method[:write_pos]))[-1]
        inject = f"""invoke-static {{{tbase}}}, {class_name}->{self.FILTER_METHOD}(Lorg/apache/thrift/TBase;)Lorg/apache/thrift/TBase;
    move-result-object {tbase}

    """
        patched_method = method[:null_check.start()] + inject + method[null_check.start():]
        return class_data.replace(method, patched_method) + self.filter_method(class_name)
