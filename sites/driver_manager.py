
class ChromeManager:
    _driver = None

    @classmethod
    def get_driver(cls):
        return cls._driver

    @classmethod
    def set_driver(cls, driver):
        cls._driver = driver
