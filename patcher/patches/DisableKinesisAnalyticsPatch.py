from .Patch import Patch
import re


class DisableKinesisAnalyticsPatch(Patch):
    """
    Patch to stop Moovit's own analytics events from being uploaded.

    Every analytics batch goes to the AWS Kinesis "AnalyticsStream", together with
    the last known GPS location of the device.
    Records of the other streams (e.g. "ServerStream") are still saved, since the app
    relies on some of them (push token, favorites, reports).

    Skipping records of the KinesisStream.ANALYTICS stream before they are saved.
    We are looking for the KinesisStreamRecorder$a class:
    .method public final a(Lz10/f;Ljava/io/ByteArrayOutputStream;)V
    from: com/moovit/aws/kinesis/KinesisStreamRecorder$a.smali
    """

    METHOD_HEADER_RE = re.compile(
        r"""
        \.method\s+public\s+final\s+\w+\((L[\w/$]+;)Ljava/io/ByteArrayOutputStream;\)V\s*
        \.locals\s+(\d+)\s*
        (?:\.param.*?\.end\s+param\s*)*
        """,
        re.VERBOSE | re.DOTALL,
    )
    STREAM_GETTER_RE = r"invoke-interface\s+\{{p1\}},\s+{record}->(\w+)\(\)Lcom/moovit/aws/kinesis/KinesisStream;"
    METHOD_INJECT = """
    invoke-interface {{p1}}, {record}->{getter}()Lcom/moovit/aws/kinesis/KinesisStream;
    move-result-object v0
    sget-object v1, Lcom/moovit/aws/kinesis/KinesisStream;->ANALYTICS:Lcom/moovit/aws/kinesis/KinesisStream;
    if-ne v0, v1, :moovit_patcher_keep_record
    return-void
    :moovit_patcher_keep_record

    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Kinesis Analytics patch..."

    def class_filter(self, class_data: str) -> bool:
        if not re.search(
            r"^\.class\b.*\sLcom/moovit/aws/kinesis/KinesisStreamRecorder\$a;",
            class_data,
            re.MULTILINE,
        ):
            return False
        keywords = [
            'saving into stream %s, partition key %s, %d bytes.',
            'Lcom/moovit/aws/kinesis/KinesisStream;',
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return True

    def class_modifier(self, class_data, class_path) -> str:
        header = self.METHOD_HEADER_RE.search(class_data)
        record_type, locals_count = header.group(1), int(header.group(2))
        # The injected code uses v0 and v1.
        assert locals_count >= 2, f"Expected at least 2 locals, got {locals_count}"
        getter = re.search(
            self.STREAM_GETTER_RE.format(record=re.escape(record_type)), class_data
        ).group(1)
        inject = self.METHOD_INJECT.format(record=record_type, getter=getter)
        return class_data[:header.end()] + inject + class_data[header.end():]
