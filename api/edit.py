from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageFilter, ImageFont, ImageDraw
import io

app = FastAPI(
    title="KingBroken Image Editor API",
    description="API ya kubadilisha picha kifalme 👑",
    version="1.0.0"
)

# CORS – ruhusu front-end yoyote itumie
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Karibu kwenye KingBroken Image Editor API 👑",
        "endpoints": ["/edit"],
        "actions": [
            "grayscale", "blur", "rotate", "flip_horizontal",
            "flip_vertical", "resize", "text"
        ]
    }

@app.post("/edit")
async def edit_image(
    file: UploadFile = File(...),
    action: str = Form(...),
    value: str = Form(None),
    width: int = Form(None),
    height: int = Form(None),
    text: str = Form(None)
):
    # Soma picha kwenye memory
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGBA")

    # Chagua action
    if action == "grayscale":
        image = image.convert("L").convert("RGBA")

    elif action == "blur":
        image = image.filter(ImageFilter.GaussianBlur(radius=5))

    elif action == "rotate":
        try:
            angle = int(value) if value else 0
        except:
            angle = 0
        image = image.rotate(angle, expand=True)

    elif action == "flip_horizontal":
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

    elif action == "flip_vertical":
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

    elif action == "resize":
        if not width or not height:
            return {"error": "Unahitaji width na height kwa resize"}
        image = image.resize((width, height))

    elif action == "text":
        if not text:
            return {"error": "Unahitaji text kwa action=text"}
        draw = ImageDraw.Draw(image)
        # Font default (system), position katikati
        w, h = image.size
        msg = text
        text_w, text_h = draw.textsize(msg)
        pos = ((w - text_w) // 2, (h - text_h) // 2)
        draw.text(pos, msg, fill=(255, 255, 255, 255))

    else:
        return {"error": "Action haijatambuliwa"}

    # Rudisha kama image (PNG)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")
