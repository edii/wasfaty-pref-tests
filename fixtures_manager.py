class FixturesManager:
    _instance = None
    _cursor = None
    _fixtures = {
        "patients": 0,
        "observations": 0,
        "organization": 0,
        "practitioner": 0,
        "encounter": 0,
        "condition": 0,
        "composition": 0,
    }

    def __init__(self):
        if FixturesManager._instance is not None:
            raise Exception("Use FixturesManager.get_instance() to access the manager.")
        FixturesManager._instance = self

    @staticmethod
    def get_instance():
        if FixturesManager._instance is None:
            FixturesManager()
        return FixturesManager._instance

    def cursor(self):
        return self._cursor

    def fixture(self, key):
        return self._fixtures.get(key)

    def set_fixture(self, key, value):
        self._fixtures[key] = value
        return self

    def set_cursor(self, cursor):
        self._cursor = cursor
        return self
