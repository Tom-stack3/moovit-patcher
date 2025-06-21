from .Patch import Patch
import re


class DisableTaxiProvidersPatch(Patch):
    """
    Patch to remove "Taxi & Ride Hailing" section.
    Acts as if there are no Taxi Providers supported.

    Patching TaxiProviderManager constructor to have empty list and map when initialized.
    We are looking for TaxiProvidersManager class:
    .method public constructor <init>(Ljava/util/List;)V
    from: com\moovit\app\taxi\providers\TaxiProvidersManager.smali
    """

    METHOD_RE = re.compile(
        r"""
        \.method\s+public\s+constructor\s+<init>\(Ljava/util/List;\)V\s*(
        .*?
        )\.end\s+method
        """,
        re.VERBOSE | re.DOTALL,
    )
    METHOD_REPLACE = """
    .locals 1
    .param p1    # Ljava/util/List;
        .annotation build Landroidx/annotation/NonNull;
        .end annotation
    .end param
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/util/List<",
            "Lcom/moovit/app/taxi/providers/TaxiProvider;",
            ">;)V"
        }
    .end annotation
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    # Initializing empty...

    invoke-static {}, Ljava/util/Collections;->emptyList()Ljava/util/List;
    move-result-object v0
    iput-object v0, p0, Lcom/moovit/app/taxi/providers/TaxiProvidersManager;->a:Ljava/util/List;

    invoke-static {}, Ljava/util/Collections;->emptyMap()Ljava/util/Map;
    move-result-object v0
    iput-object p1, p0, Lcom/moovit/app/taxi/providers/TaxiProvidersManager;->b:Ljava/util/Map;

    return-void
    """

    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)
        self.print_message = "[+] Applying Disable Taxi Providers patch..."

    def class_filter(self, class_data: str) -> bool:
        keywords = [
            'TaxiProvidersManager',
            'TaxiProvider',
            'providers',
            'taxi_providers_manager',
        ]
        for k in keywords:
            if k not in class_data:
                return False
        return True

    def class_modifier(self, class_data, class_path) -> str:
        method_body = self.METHOD_RE.findall(class_data)[0]
        return class_data.replace(
            method_body,
            self.METHOD_REPLACE,
        )
