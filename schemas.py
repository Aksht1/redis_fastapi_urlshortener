from pydantic import BaseModel, HttpUrl


class URLCreate(BaseModel):
    original_url: HttpUrl


class URLResponse(BaseModel):
    original_url: str
    short_url: str