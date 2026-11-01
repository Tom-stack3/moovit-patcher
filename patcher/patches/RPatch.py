from .Patch import Patch


class RPatch(Patch):
    # Moovit's google_api_key resource, rotated between releases (5.145: AIzaSyA3jYXo-...).
    MOOVIT_GOOGLE_API_KEY = b"AIzaSyCO5ioIA3IfeMEjIXwa2yIhAWA-12evCn0"

    def __init__(self, extracted_path, custom_google_api_key):
        super().__init__(extracted_path, is_multi_class=False)
        self.custom_google_api_key = custom_google_api_key.encode()

    def class_modifier(self, class_data, class_path) -> str:
        return class_data.replace(
            b"Accessibility Statement",
            b"Ninja turtles          ",
        ).replace(
            b"Where do you want to go?",
            b"Expensive bro, where to?",
        ).replace(
            RPatch.MOOVIT_GOOGLE_API_KEY,
            self.custom_google_api_key,
        )
