import string
import random

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import URL
from schemas import URLCreate, URLResponse


app = FastAPI(title="Simple URL Shortener")


# Create SQLite tables
Base.metadata.create_all(bind=engine)


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits

    return "".join(
        random.choice(characters)
        for _ in range(length)
    )


@app.post("/shorten", response_model=URLResponse)
def shorten_url(
    data: URLCreate,
    db: Session = Depends(get_db)
):
    short_code = generate_short_code()

    # Make sure the generated code is unique
    while db.query(URL).filter(
        URL.short_code == short_code
    ).first():
        short_code = generate_short_code()

    url = URL(
        original_url=str(data.original_url),
        short_code=short_code
    )

    db.add(url)
    db.commit()
    db.refresh(url)

    return {
        "original_url": url.original_url,
        "short_url": f"http://localhost:8000/{url.short_code}"
    }


@app.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    db: Session = Depends(get_db)
):
    url = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    return RedirectResponse(url.original_url)