from fastapi import FastAPI, File, UploadFile, Request, Form
import shutil
import os
import uvicorn 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..src import main
app = FastAPI()



UPLOAD_DIR = "data\papers"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def upload(request: Request):
   return templates.TemplateResponse("../template/index.html", {"request": request})


@app.post("/uploader/")
async def upload_research_paper(file: UploadFile = File(...)):
    # Define save path
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save uploaded file
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "content_type": file.content_type, "saved_to": save_path}

@app.post("/submit")
async def submit(query: str = Form(...)):
   response = main(query)
   return {"response":response}
if __name__ == "__main__":
    uvicorn.run("main:app",host = "127.0.0.1", port = 8000, reload = True)