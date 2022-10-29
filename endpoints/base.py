from databases import Database


class BaseRouter:

    def __init__(self, database: Database):
        self.database = database
        