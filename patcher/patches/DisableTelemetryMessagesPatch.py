from .Patch import Patch
import re


class DisableTelemetryMessagesPatch(Patch):
    """
    Patch to stop device telemetry messages sent over the Kinesis "ServerStream".

    Dropped messages (by the type of the MVServerMessage union value):
    - MVStaticMetricsServerMessage: device model, build, CPU, RAM, storage, sensors, display.
    - MVDynamicMetricsServerMessage: OS, timezone, memory, networks, carrier, battery, app permissions.
    - MVSetAdvertisingInfoRequest: AppsFlyer ID, App Set ID, limit ad tracking flag.
    - MVApplicationInfos: list of installed applications (unused in 5.145, dropped just in case).

    A record that writes no bytes is not saved by KinesisStreamRecorder.
    We are looking for the ThriftKinesisable class:
    .method public final a(Ljava/io/OutputStream;)V
    from: z10/j.smali
    """

    TBASE_RESULT_RE = re.compile(
        r"""
        \.method\s+public\s+final\s+\w+\(Ljava/io/OutputStream;\)V\s*
        \.locals\s+(\d+)\s*
        .*?
        invoke-virtual\s+\{p0\},\s+L[\w/$]+;->\w+\(\)Lorg/apache/thrift/TBase;\s*
        (?:\.line\s+\d+\s*)*
        move-result-object\s+(v\d+)\s*
        """,
        re.VERBOSE | re.DOTALL,
    )
    DROPPED_TYPES = [
        "Lcom/tranzmate/moovit/protocol/metrics/MVStaticMetricsServerMessage;",
        "Lcom/tranzmate/moovit/protocol/metrics/MVDynamicMetricsServerMessage;",
        "Lcom/tranzmate/moovit/protocol/users/MVSetAdvertisingInfoRequest;",
        "Lcom/tranzmate/moovit/protocol/datacollection/MVApplicationInfos;",
    ]

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
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
        return True

    def class_modifier(self, class_data, class_path) -> str:
        match = self.TBASE_RESULT_RE.search(class_data)
        locals_count, tbase = int(match.group(1)), match.group(2)
        # The injected code uses v1 and v2 as temporaries, the TBase must be in v0.
        assert tbase == "v0" and locals_count >= 3, f"Unexpected registers: {tbase}, {locals_count} locals"
        checks = "".join(
            f"""
    instance-of v2, v1, {t}
    if-nez v2, :moovit_patcher_drop_message
""" for t in self.DROPPED_TYPES
        )
        inject = f"""
    instance-of v1, v0, Lcom/tranzmate/moovit/protocol/kinesis/MVServerMessage;
    if-eqz v1, :moovit_patcher_keep_message
    move-object v1, v0
    check-cast v1, Lorg/apache/thrift/TUnion;
    invoke-virtual {{v1}}, Lorg/apache/thrift/TUnion;->h()Ljava/lang/Object;
    move-result-object v1
{checks}
    goto :moovit_patcher_keep_message
    :moovit_patcher_drop_message
    return-void
    :moovit_patcher_keep_message

"""
        return class_data[:match.end()] + inject + class_data[match.end():]
