"""
一键生成分层报告的命令行工具（支持 PDF / DOCX）

支持从 TXT/DOCX/PDF 输入解析题目与答案，进行分类并输出报告。
可选择输出格式（PDF/DOCX），并按“综合难度评分”降序排序。

TXT 文本格式示例：

题目：已知某弱酸的电离常数为 Ka=1.8e-5，计算其在0.1mol/L 溶液中的 pH。
答案：pH≈2.9

（题目块之间使用空行分隔）
"""

import argparse
import logging
from pathlib import Path
from typing import List, Tuple

import sys
from pathlib import Path

# Ensure both local src and embedded classifier package are importable
_BASE_DIR = Path(__file__).resolve().parents[2]
_EXTRA_PATHS = [
    _BASE_DIR / "src",
    _BASE_DIR / "chemistry-homework-classifier" / "src",
]
for _p in _EXTRA_PATHS:
    _p_str = str(_p)
    if _p.exists() and _p_str not in sys.path:
        sys.path.insert(0, _p_str)

try:
    from difficulty_assessor.classifier import ThreeTierClassifier
except ImportError:
    import importlib.util
    _CC_SRC = _BASE_DIR / "chemistry-homework-classifier" / "src"

    def _load_module(module_name: str, file_path: Path, package_dir: Path = None):
        if package_dir is not None:
            spec = importlib.util.spec_from_file_location(
                module_name, str(file_path), submodule_search_locations=[str(package_dir)]
            )
        else:
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    _load_module("src.data", _CC_SRC / "data" / "__init__.py", _CC_SRC / "data")
    _load_module("src.data.chemistry_vocab", _CC_SRC / "data" / "chemistry_vocab" / "__init__.py", _CC_SRC / "data" / "chemistry_vocab")
    _load_module("src.difficulty_assessor.assessor", _CC_SRC / "difficulty_assessor" / "assessor.py")
    _classifier_mod = _load_module("src.difficulty_assessor.classifier", _CC_SRC / "difficulty_assessor" / "classifier.py")
    ThreeTierClassifier = _classifier_mod.ThreeTierClassifier


logger = logging.getLogger(__name__)


def _extract_text(path: Path) -> str:
    """根据扩展名提取文本内容，支持 .txt/.docx/.pdf"""
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8")
    elif suffix == ".docx":
        try:
            import docx  # type: ignore
            doc = docx.Document(str(path))
            return "\n".join(p.text or "" for p in doc.paragraphs)
        except Exception as e:
            raise SystemExit(f"无法解析DOCX文本：{e}")
    elif suffix == ".pdf":
        try:
            import pdfplumber  # type: ignore
            with pdfplumber.open(str(path)) as pdf:
                pages_text = [p.extract_text() or "" for p in pdf.pages]
            return "\n\n".join(pages_text)
        except Exception as e:
            raise SystemExit(f"无法解析PDF文本：{e}")
    else:
        # 尝试作为UTF-8文本读取
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            raise SystemExit("不支持的输入文件格式，仅支持 TXT / DOCX / PDF")


def parse_questions_text(content: str) -> List[Tuple[str, str]]:
    """从原始文本解析题目与答案列表。
    返回列表，每项为 (question_text, answer_text)，若无答案则第二项为空字符串。
    """
    blocks: List[str] = []
    current: List[str] = []
    for line in content.splitlines():
        if line.strip():
            current.append(line)
        else:
            if current:
                blocks.append("\n".join(current))
                current = []
    if current:
        blocks.append("\n".join(current))

    pairs: List[Tuple[str, str]] = []
    for b in blocks:
        q = []
        a = []
        for ln in b.splitlines():
            if ln.strip().startswith("答案：") or ln.strip().startswith("答案:"):
                a.append(ln.split("：", 1)[-1] if "：" in ln else ln.split(":", 1)[-1])
            elif ln.strip().startswith("题目：") or ln.strip().startswith("题目:"):
                q.append(ln.split("：", 1)[-1] if "：" in ln else ln.split(":", 1)[-1])
            else:
                q.append(ln)
        question_text = "\n".join(q).strip()
        answer_text = "\n".join(a).strip()
        if question_text:
            pairs.append((question_text, answer_text))

    return pairs


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="一键生成分层报告（PDF/DOCX）")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("examples/questions.txt"),
        help="输入文件路径（支持 TXT/DOCX/PDF；默认：examples/questions.txt）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("examples/classified_report.pdf"),
        help="输出文件路径（默认：examples/classified_report.pdf 或 .docx）",
    )
    parser.add_argument(
        "--format",
        choices=["pdf", "docx"],
        default="pdf",
        help="输出格式（pdf 或 docx）",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="高中化学分层作业报告",
        help="报告标题",
    )
    parser.add_argument(
        "--author",
        type=str,
        default="chemistry-homework-classifier",
        help="报告作者",
    )
    parser.add_argument(
        "--font-path",
        type=Path,
        default=None,
        help="可选中文TTF字体路径（如 NotoSansSC-Regular.ttf）",
    )
    parser.add_argument(
        "--sort-by-score",
        action="store_true",
        help="按综合难度评分降序排序（默认开启）",
    )
    parser.set_defaults(sort_by_score=True)
    return parser.parse_args()


def main():
    args = build_args()
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    # 检查输入文件
    if not args.input.exists():
        logger.warning(f"未找到输入文件：{args.input}，将使用默认示例题目。")
        default_text = (
            "题目：已知某弱酸的电离常数为 Ka=1.8e-5，计算其在0.1mol/L 溶液中的 pH。\n"
            "答案：pH≈2.9\n\n"
            "题目：比较甲烷与乙烷的分子结构与物理性质差异，并说明原因。\n\n"
            "题目：设计实验测定某反应的活化能，并讨论误差来源。\n"
        )
        args.input.parent.mkdir(parents=True, exist_ok=True)
        args.input.write_text(default_text, encoding="utf-8")

    content = _extract_text(args.input)
    pairs = parse_questions_text(content)
    if not pairs:
        raise SystemExit("输入文件未解析到题目内容，请检查格式。")

    # 分类
    classifier = ThreeTierClassifier()
    # 延迟导入输出模块，避免依赖缺失时整个CLI无法启动
    try:
        # 直接按文件路径加载，避免相对导入上下文问题
        _OG_PKG = _BASE_DIR / "src" / "output_generator"
        _og_pdf = _load_module("src.output_generator.pdf_generator", _OG_PKG / "pdf_generator.py")
        ClassifiedQuestion = _og_pdf.ClassifiedQuestion
        ClassifiedPDFGenerator = _og_pdf.ClassifiedPDFGenerator
        PDFReportStyle = _og_pdf.PDFReportStyle
        create_pdf = getattr(_og_pdf, "create_pdf", None)
        create_pdf_sorted = getattr(_og_pdf, "create_pdf_sorted", None)

        # 可选DOCX生成器
        try:
            _og_docx = _load_module("src.output_generator.docx_generator", _OG_PKG / "docx_generator.py")
            create_docx_sorted = getattr(_og_docx, "create_docx_sorted", None)
        except Exception:
            create_docx_sorted = None
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise SystemExit(
            "输出模块导入失败，请先安装依赖：\n"
            "  python -m pip install -r requirements.txt\n"
            f"错误详情：{e}\n"
            f"Traceback:\n{tb}"
        )

    items: List[ClassifiedQuestion] = []
    for q, a in pairs:
        res = classifier.classify_question(q, a or None)
        items.append(ClassifiedQuestion(question_text=q, answer_text=a or None, classification=res))

    # 根据格式输出
    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "pdf":
        style = PDFReportStyle(title=args.title, author=args.author, font_path=str(args.font_path) if args.font_path else None)
        generator = ClassifiedPDFGenerator(style=style)
        # 扩展名修正
        if args.output.suffix.lower() != ".pdf":
            args.output = args.output.with_suffix(".pdf")
        if args.sort_by_score:
            generator.generate_sorted_report(str(args.output), items, metadata={
                "subtitle": "自动生成的分层与难度分析",
                "sort_note": "排序依据：综合难度评分降序",
            })
        else:
            generator.generate_report(str(args.output), items, metadata={
                "subtitle": "自动生成的分层与难度分析",
            })
    else:  # docx
        if create_docx_sorted is None:
            raise SystemExit("DOCX生成功能不可用，请确认已安装 python-docx 依赖")
        if args.output.suffix.lower() != ".docx":
            args.output = args.output.with_suffix(".docx")
        create_docx_sorted(str(args.output), items, metadata={
            "subtitle": "自动生成的分层与难度分析",
        })

    print(f"生成完成：{args.output}")


if __name__ == "__main__":
    main()