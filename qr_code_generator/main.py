from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import qrcode
import io

app = FastAPI()

@app.get("/qrcode")
def generate_qr(text: str = Query(..., description="Text or URL to encode")):
    qr = qrcode.make(text)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
