import pydantic


class User(pydantic.BaseModel):
    id: int
    group: str | None
