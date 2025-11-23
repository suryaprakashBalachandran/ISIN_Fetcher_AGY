
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
from utils import fetch_isin
import uvicorn
import csv
import io

app = FastAPI(title="ISIN Fetcher API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ISINRequest(BaseModel):
    queries: List[str]

class ISINResponse(BaseModel):
    query: str
    isin: Optional[str]
    source: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    from fastapi.responses import Response
    with open("static/index.html", "r") as f:
        content = f.read()
    return Response(
        content=content,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@app.post("/upload-csv", response_model=List[ISINResponse])
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Read CSV file
    contents = await file.read()
    csv_file = io.StringIO(contents.decode('utf-8'))
    csv_reader = csv.reader(csv_file)
    
    # Extract queries (handle both with and without headers)
    queries = []
    rows = list(csv_reader)
    
    # Check if first row looks like a header
    if rows and any(keyword in rows[0][0].lower() for keyword in ['name', 'company', 'fund', 'stock', 'query']):
        rows = rows[1:]  # Skip header
    
    # Extract first column values
    for row in rows:
        if row and row[0].strip():
            queries.append(row[0].strip())
    
    # Fetch ISINs
    results = []
    for q in queries:
        res = fetch_isin(q)
        results.append(ISINResponse(
            query=res['query'],
            isin=res['isin'],
            source=res['source']
        ))
    
    return results

@app.post("/fetch-isins", response_model=List[ISINResponse])
async def get_isins(request: ISINRequest):
    results = []
    for q in request.queries:
        # We process sequentially for now. For production, async/parallel processing is better.
        # Since fetch_isin uses blocking requests, we should ideally run it in a threadpool.
        # But for this simple app, sequential is fine or we can use fastAPI's concurrency.
        # FastAPI runs normal def functions in a threadpool automatically.
        res = fetch_isin(q)
        results.append(ISINResponse(
            query=res['query'],
            isin=res['isin'],
            source=res['source']
        ))
    return results



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
