import time
import redis.asyncio as redis

from pathlib import Path
from typing import Annotated

import uvicorn
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request,
    Form,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.db import get_db
from src.routes import contacts, auth, users, documents, sms
from src.conf.config import settings
from src.services.email.mail import send_email_contact_form as send_email


app = FastAPI()


@app.on_event("startup")
async def startup():
    print("------------- STARTUP --------------")
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


origins = ["http://only-nance-goit.koyeb.app"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    during = time.time() - start_time
    response.headers["performance"] = str(during)
    return response


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a function that returns the message &quot;
    Welcome to FastAPI!&quot; if the database connection is successful.

    :param db: Session: Get the database session from the dependency
    :return: A dictionary with a message
    :doc-author: Ihor Voitiuk
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )


templates = Jinja2Templates(directory="templates")
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    The root function is the entry point for the application.
    It returns a Jinja2 template response, which will be rendered by
    the Jinja2 engine and returned to the client.

    :param request: Request: Get the request object that is sent to the server
    :return: A templateresponse object, which is a special type of response
    :doc-author: Ihor Voitiuk
    """
    context = {"docs_url": f"{origins[0]}/docs"}
    return templates.TemplateResponse(
        "index.html", {"request": request, "context": context}
    )


@app.post("/", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    name: str = Form(title="Name", description="Your full name"),
    email: str = Form(title="Email", description="Your email address"),
    phone: str = Form(title="Phone", description="Your phone number"),
    message: str = Form(title="Message", description="Your message"),
):
    """
    The submit_form function is a POST endpoint that accepts the form
    data and sends an email to the configured address.

    :param request: Request: Get the request object for the current http request
    :param name: str: Get the name from the form
    :param description: Provide a description for the field
    :param email: str: Get the email address of the person who is submitting a message
    :param description: Provide a description for the form field
    :param phone: str: Get the phone number from the form
    :param description: Provide a description for the field
    :param message: str: Get the message from the form
    :param description: Provide a description for the field
    :param : Get the request object
    :return: A templateresponse object
    :doc-author: Ihor Voitiuk
    """
    context = {"docs_url": f"{origins[0]}/docs"}
    if not name or not email or not phone or not message:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "context": context,
                "error_message": "All fields are required.",
            },
        )
    await send_email(email, name, phone, message, subj="Contact form")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "context": context,
            "success_message": "Message sent successfully!",
        },
    )


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(sms.router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
