from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import BASE_DIR, get_settings
from .database import Base, engine
from .routers import api, auth, pages

settings=get_settings()
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app=FastAPI(title=settings.app_name,version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.mount("/static",StaticFiles(directory=str(BASE_DIR/"app"/"static")),name="static")
app.include_router(pages.router); app.include_router(auth.router); app.include_router(api.router)

@app.get("/health")
def health(): return {"status":"ok","app":settings.app_name,"gemini_configured":bool(settings.gemini_api_key and settings.use_gemini),"model":settings.gemini_model}

@app.get("/startup")
def startup_status(): return health()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app",host="127.0.0.1",port=8000,reload=True)
