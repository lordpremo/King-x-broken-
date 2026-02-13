from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
import io

app = FastAPI(
    title="KingBroken Image Editor API",
    description="API ya kubadilisha picha kifalme 👑",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def to_png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

def apply_sepia(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    width, height = img.size
    pixels = img.load()
    for py in range(height):
        for px in range(width):
            r, g, b = pixels[px, py]
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))
    return img.convert("RGBA")

def apply_vignette(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size
    vignette = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(vignette)
    max_radius = max(w, h)
    for i in range(int(max_radius * 1.2)):
        alpha = int(255 * (i / (max_radius * 1.2)))
        draw.ellipse(
            (-i, -i, w + i, h + i),
            fill=alpha
        )
    vignette = vignette.resize((w, h))
    black = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    img = Image.composite(black, img, vignette)
    return img

@app.get("/")
def home():
    return {
        "message": "Karibu kwenye KingBroken Image Editor API 👑",
        "endpoint": "/edit",
        "actions": [
            "grayscale",
            "invert",
            "blur",
            "strong_blur",
            "sharpen",
            "contour",
            "edge_enhance",
            "emboss",
            "sepia",
            "brightness_up",
            "brightness_down",
            "contrast_up",
            "contrast_down",
            "rotate",
            "flip_horizontal",
            "flip_vertical",
            "resize",
            "text",
            "watermark",
            "royal_preset",
            "dark_preset"
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
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGBA")
    except Exception:
        return JSONResponse({"error": "Picha haikusomeka"}, status_code=400)

    try:
        if action == "grayscale":
            image = image.convert("L").convert("RGBA")

        elif action == "invert":
            image = ImageOps.invert(image.convert("RGB")).convert("RGBA")

        elif action == "blur":
            image = image.filter(ImageFilter.GaussianBlur(radius=3))

        elif action == "strong_blur":
            image = image.filter(ImageFilter.GaussianBlur(radius=8))

        elif action == "sharpen":
            image = image.filter(ImageFilter.SHARPEN)

        elif action == "contour":
            image = image.filter(ImageFilter.CONTOUR)

        elif action == "edge_enhance":
            image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)

        elif action == "emboss":
            image = image.filter(ImageFilter.EMBOSS)

        elif action == "sepia":
            image = apply_sepia(image)

        elif action == "brightness_up":
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.4)

        elif action == "brightness_down":
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(0.6)

        elif action == "contrast_up":
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)

        elif action == "contrast_down":
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(0.7)

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
                return JSONResponse(
                    {"error": "Unahitaji width na height kwa resize"},
                    status_code=400
                )
            image = image.resize((width, height))

        elif action == "text":
            if not text:
                return JSONResponse(
                    {"error": "Unahitaji text kwa action=text"},
                    status_code=400
                )
            draw = ImageDraw.Draw(image)
            w, h = image.size
            msg = text
            tw, th = draw.textsize(msg)
            pos = ((w - tw) // 2, (h - th) // 2)
            draw.text(pos, msg, fill=(255, 255, 255, 255))

        elif action == "watermark":
            wm_text = text if text else "King Broken 👑"
            draw = ImageDraw.Draw(image)
            w, h = image.size
            tw, th = draw.textsize(wm_text)
            pos = (w - tw - 10, h - th - 10)
            draw.text(pos, wm_text, fill=(255, 255, 255, 160))

        elif action == "royal_preset":
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.3)
            image = image.filter(ImageFilter.GaussianBlur(radius=1.2))
            draw = ImageDraw.Draw(image)
            w, h = image.size
            msg = text if text else "King Broken 👑"
            tw, th = draw.textsize(msg)
            pos = ((w - tw) // 2, h - th - 20)
            draw.text(pos, msg, fill=(255, 215, 0, 230))

        elif action == "dark_preset":
            image = image.convert("L").convert("RGBA")
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.4)
            image = apply_vignette(image)

        else:
            return JSONResponse({"error": "Action haijatambuliwa"}, status_code=400)

        png_bytes = to_png_bytes(image)
        return Response(content=png_bytes, media_type="image/png")

    except Exception as e:
        return JSONResponse({"error": f"Hitilafu wakati wa kuchakata: {str(e)}"}, status_code=500)
