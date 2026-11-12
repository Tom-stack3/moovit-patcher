from ..Patch import Patch
import re


class DisableKinesisAnalyticsPatch(Patch):
    """
    Patch to stop Moovit's own analytics events from being uploaded.

    Every analytics batch goes to the AWS Kinesis "AnalyticsStream", together with
    the last known GPS location of the device.
    Records of the other streams (e.g. "ServerStream") are still saved, since the app
    relies on some of them (push token, favorites, reports).

    Skipping records of the KinesisStream.ANALYTICS stream before they are saved,
    the same way the app skips records of a stream it has no name for.
    We are looking for the KinesisStreamRecorder class:
    .method public final a(Lz1a;Ljava/io/ByteArrayOutputStream;Lkotlin/coroutines/jvm/internal/ContinuationImpl;)Ljava/lang/Object;
    from: com/moovit/core/aws/kinesis/f.smali
    """

    # Only reached on the first call (not when the coroutine resumes), where p1 is the record.
    # The register written right after is free to use.
    STREAM_RE = re.compile(
        r"""
        (invoke-interface\s+\{p1\},\s+L[\w/$]+;->\w+\(\)(L[\w/$]+/KinesisStream;)\s*
        (?:\.line\s+\d+\s*)*
        move-result-object\s+(\w+)\s*)
        (?:\.line\s+\d+\s*)*
        (?:iget-object|sget-object|const-string|move-result-object)\s+(v\d+),
        """,
        re.VERBOSE,
    )
    UNIT_RE = re.compile(r"sget-object\s+\w+,\s+(Lkotlin/Unit;->\w+:Lkotlin/Unit;)")
    INJECT = """
    sget-object {free}, {stream}->ANALYTICS:{stream}
    if-ne {value}, {free}, :moovit_patcher_keep_record
    sget-object {free}, {unit}
    return-object {free}
    :moovit_patcher_keep_record

    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Kinesis Analytics patch..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            '"saving into stream "',
            '", partition key "',
            'Lcom/amazonaws/mobileconnectors/kinesis/kinesisrecorder/KinesisRecorder;->saveRecord([BLjava/lang/String;)V',
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return len(self.STREAM_RE.findall(class_data)) == 1

    def class_modifier(self, class_data, class_path) -> str:
        match = self.STREAM_RE.search(class_data)
        _, stream, value, free = match.groups()
        unit = self.UNIT_RE.search(class_data).group(1)
        inject = self.INJECT.format(free=free, stream=stream, value=value, unit=unit)
        return class_data[:match.end(1)] + inject + class_data[match.end(1):]
