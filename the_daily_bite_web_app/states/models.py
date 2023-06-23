import pynecone as pc


class User(pc.Model, table=True):
    user_id: str
    name: str
