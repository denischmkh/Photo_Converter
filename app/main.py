import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
import rawpy
from pathlib import Path
from fastapi import Request

app = FastAPI()

# Настройка папки для сохранения изображений
UPLOAD_FOLDER = Path("app/static/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Настройка шаблонов для загрузки
templates = Jinja2Templates(directory="app/templates")

# Путь для доступа к сохраненным изображениям
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def convert_raw_to_jpeg(input_path: Path, output_path: Path):
    """Конвертируем RAW или CR2 файл в JPEG"""
    if input_path.suffix.lower() == '.cr2':
        with rawpy.imread(str(input_path)) as raw:
            rgb = raw.postprocess()
            img = Image.fromarray(rgb)
            img.save(output_path, 'JPEG')
    else:
        # Для других RAW форматов (например, .NEF) можно добавить обработку здесь
        img = Image.open(input_path)
        img.convert('RGB').save(output_path, 'JPEG')


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Сохраняем файл
    file_path = UPLOAD_FOLDER / "IMG.CR2"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Конвертируем в JPEG
    output_path = UPLOAD_FOLDER / f"IMG.jpeg"
    convert_raw_to_jpeg(file_path, output_path)

    # Отправляем обратно файл
    return FileResponse(output_path, media_type='image/jpeg')