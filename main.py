from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from api.v1.router import api_router


app = FastAPI(title="Complete Auth FastAPI")

app.include_router(api_router, prefix="/api/v1")


# Serve a simple static reset-password HTML page for local testing
@app.get("/reset-password")
def reset_password_page():
	html_path = Path(__file__).resolve().parent / "static" / "reset-password.html"
	return FileResponse(html_path, media_type="text/html")
