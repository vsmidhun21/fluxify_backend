from io import BytesIO
from PIL import Image
import img2pdf

def compress_image(file_bytes: bytes, quality: int = 75, max_width: int | None = None) -> bytes:
    img = Image.open(BytesIO(file_bytes))
    # convert to RGB for JPEG
    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # resize if requested
    if max_width and img.width > max_width:
        ratio = max_width / img.width
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    out = BytesIO()
    img.save(out, format="JPEG", quality=quality, optimize=True)
    out.seek(0)
    return out.read()

def convert_format(file_bytes: bytes, target_format: str = "PNG") -> bytes:
    img = Image.open(BytesIO(file_bytes))
    out = BytesIO()
    tf = target_format.upper()
    if tf == "PNG":
        img.save(out, format="PNG")
    else:
        # ensure RGB for non-PNGs
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert("RGB")
        if tf in ("JPG", "JPEG"):
            img.save(out, format="JPEG")
        elif tf == "WEBP":
            img.save(out, format="WEBP")
        else:
            img.save(out, format=tf)
    out.seek(0)
    return out.read()

def image_to_pdf(file_bytes: bytes) -> bytes:
    # img2pdf can convert raw bytes (single image) to PDF bytes
    # if you want to support multi-page or multiple files, change the API accordingly
    return img2pdf.convert(file_bytes)
