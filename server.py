from fastapi import FastAPI, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel
from typing import Optional
import random
import string

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connection = sqlite3.connect("links.db")
cursor = connection.cursor()

BASE_DOMAIN = "https://example.com/"
LENGTH = 5


class LinkBody(BaseModel):
    id: Optional[str] = Form(None)
    link: str = Form(...)


@app.get("/{link_id}")
async def root(link_id):
    ids = cursor.execute("SELECT * FROM links").fetchall()
    found = False
    site_link = ""

    for id, link in ids:
        if id == link_id:
            found = True
            site_link = link
            break

    if not found:
        raise HTTPException(status_code=404, detail="That link doesn't exist!")

    print(f"Redirecting to {site_link}")
    return RedirectResponse(site_link)


@app.post("/api/create")
async def createLink(linkbody: LinkBody):
    print(f"Received: " + str(linkbody.__dict__))
    if not linkbody.id:
        linkbody.id = "".join(
            random.SystemRandom().choice(string.ascii_lowercase + string.digits)
            for _ in range(LENGTH)
        )
    ids = cursor.execute("SELECT * FROM links").fetchall()
    for id in ids:
        print(id)
        if id[0] == linkbody.id:
            raise HTTPException(status_code=400, detail="ID already exists")
        if id[1] == linkbody.link:
            raise HTTPException(status_code=400, detail="Site link already exists")

    cursor.execute("INSERT INTO links VALUES (?, ?)", (linkbody.id, linkbody.link))
    connection.commit()
    return {"link": f"{BASE_DOMAIN}{linkbody.id}"}
