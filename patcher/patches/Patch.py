class Patch:
    def __init__(self, extracted_path, is_multi_class=False):
        self.extracted_path = extracted_path
        self.print_message = "Applying patch..."
        self.class_data = []
        self.class_path = []
        self.is_multi_class = is_multi_class

    def class_filter(self, class_data: str) -> bool:
        raise NotImplementedError

    def class_modifier(self, class_data: str, class_path: str) -> str:
        raise NotImplementedError
