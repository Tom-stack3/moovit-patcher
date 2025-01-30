from .Patch import Patch


class LPatch(Patch):
    def __init__(self, extracted_path):
        super().__init__(extracted_path, is_multi_class=False)

    def class_modifier(self, class_data, class_path) -> str:
        return class_data.replace(
            b"Accessibility Statement",
            b"Ninja turtles          ",
        ).replace(
            b"Where do you want to go?",
            b"Expensive bro, where to?",
        )
