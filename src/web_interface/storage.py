from pathlib import Path
from typing import Tuple
from io import BytesIO
import time

from werkzeug.utils import secure_filename

ALLOWED_EXTS = {".txt", ".pdf", ".docx"}


def ensure_storage_base(base_dir: Path) -> Tuple[Path, Path, Path]:
    base_dir.mkdir(parents=True, exist_ok=True)
    txt_dir = base_dir / "txt"
    pdf_dir = base_dir / "pdf"
    docx_dir = base_dir / "docx"
    txt_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    docx_dir.mkdir(parents=True, exist_ok=True)
    return txt_dir, pdf_dir, docx_dir


def classify_and_validate(file_bytes: bytes, filename: str) -> str:
    """Validate file by extension and basic structure; return type: 'txt'|'pdf'|'docx'.

    Raises ValueError if unsupported or invalid.
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise ValueError("仅支持TXT、PDF和DOCX格式")

    if ext == ".txt":
        # Basic decode check
        try:
            file_bytes.decode("utf-8")
        except Exception:
            try:
                file_bytes.decode("gbk")
            except Exception:
                # Fallback: allow but could be binary
                pass
        return "txt"

    if ext == ".pdf":
        try:
            from PyPDF2 import PdfReader  # type: ignore
            reader = PdfReader(BytesIO(file_bytes))
            # Ensure at least one page
            if len(reader.pages) <= 0:
                raise ValueError("PDF文件无效：无页面")
            return "pdf"
        except Exception as e:
            raise ValueError(f"PDF文件无效：{e}")

    if ext == ".docx":
        try:
            import docx  # type: ignore
            _ = docx.Document(BytesIO(file_bytes))
            return "docx"
        except Exception as e:
            raise ValueError(f"DOCX文件无效：{e}")

    # Should not reach here
    raise ValueError("仅支持TXT、PDF和DOCX格式")


def save_file(file_bytes: bytes, filename: str, base_dir: Path) -> Path:
    """Save file into typed subdir based on extension; return path.
    Creates a unique filename to avoid collisions.
    """
    file_type = classify_and_validate(file_bytes, filename)
    txt_dir, pdf_dir, docx_dir = ensure_storage_base(base_dir)
    safe_name = secure_filename(filename) or f"upload{Path(filename).suffix.lower()}"
    ts = time.strftime("%Y%m%d_%H%M%S")
    target_dir = txt_dir if file_type == "txt" else pdf_dir if file_type == "pdf" else docx_dir
    target_path = target_dir / f"{ts}_{safe_name}"
    target_path.write_bytes(file_bytes)
    return target_path