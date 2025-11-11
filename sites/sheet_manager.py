
class SheetManager:
    _sheet = None

    @classmethod
    def get_sheet(cls):
        return cls._sheet

    @classmethod
    def set_sheet(cls, sheet):
        cls._sheet = sheet