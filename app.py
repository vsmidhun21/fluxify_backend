import os
from flask import Flask, request, send_file, abort
from io import BytesIO
from utils import compress_image, convert_format, image_to_pdf
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/')
def index():
    return 'Web App with Python Flask!'

@app.route("/compress", methods=["POST"])
def compress():
    if "file" not in request.files:
        abort(400, "No file part")
    file = request.files["file"]
    try:
        quality = int(request.form.get("quality", 75))
    except Exception:
        quality = 75
    try:
        max_width = request.form.get("max_width", None)
        max_width = int(max_width) if max_width not in (None, "", "null") else None
    except Exception:
        max_width = None

    in_bytes = file.read()
    try:
        out_bytes = compress_image(in_bytes, quality=quality, max_width=max_width)
    except Exception as e:
        abort(400, str(e))

    filename = file.filename.replace("\\", "/")
    base = filename.rsplit("/", 1)[-1].rsplit(".", 1)[0]

    return send_file(
        BytesIO(out_bytes),
        mimetype="image/jpeg",
        as_attachment=True,
        download_name=f"compressed_{base}.jpg"
    )


@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        abort(400, "No file part")
    file = request.files["file"]
    fmt = (request.form.get("format") or "PNG").upper()

    in_bytes = file.read()
    try:
        out_bytes = convert_format(in_bytes, target_format=fmt)
    except Exception as e:
        abort(400, str(e))

    # map format to mimetype
    mimetype = "image/png"
    if fmt in ("JPG", "JPEG"):
        mimetype = "image/jpeg"
    elif fmt == "WEBP":
        mimetype = "image/webp"
    elif fmt == "GIF":
        mimetype = "image/gif"

    ext = fmt.lower() if fmt != "JPEG" else "jpg"
    
    base = os.path.splitext(os.path.basename(file.filename))[0]

    return send_file(
        BytesIO(out_bytes),
        mimetype=mimetype,
        as_attachment=True,
        download_name=f"converted_{base}.{ext}"
    )


@app.route("/to-pdf", methods=["POST"])
def to_pdf():
    if "file" not in request.files:
        abort(400, "No file part")
    file = request.files["file"]

    in_bytes = file.read()
    try:
        pdf_bytes = image_to_pdf(in_bytes)
    except Exception as e:
        abort(400, str(e))

    # Safe filename
    base = os.path.splitext(os.path.basename(file.filename))[0]

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{base}.pdf"
    )


@app.route('/test' , methods=["GET"])
def test():
    return 'Web App with Python Flask! Testing endpoint working fine.'


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # debug=False in production
    app.run(host="0.0.0.0", port=port, debug=False)

