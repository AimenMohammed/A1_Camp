from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers import users, projects, tasks # استيراد المجلد كحزمة
from database import engine, Base

Base.metadata.create_all(bind=engine)
                         
app = FastAPI(title="FastAPI Dashboard")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
