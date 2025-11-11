"""
分层PDF输出生成器
使用 reportlab 生成结构化的分层化学作业报告
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import html

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    ListFlowable,
    ListItem,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.difficulty_assessor.classifier import ClassificationResult, DifficultyLevel


logger = logging.getLogger(__name__)


@dataclass
class ClassifiedQuestion:
    question_text: str
    classification: ClassificationResult
    answer_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None  # e.g., {"question_id": "Q123", "knowledge_tags": ["酸碱", "平衡"]}


@dataclass
class PDFReportStyle:
    title: str = "高中化学分层作业"
    author: str = "chemistry-homework-classifier"
    font_name: str = "STSong-Light"
    font_path: Optional[str] = None
    page_size: Any = A4
    margin_left: float = 36
    margin_right: float = 36
    margin_top: float = 48
    margin_bottom: float = 48
    primary_color: Any = colors.HexColor("#1f6feb")
    secondary_color: Any = colors.HexColor("#2ea043")


class ClassifiedPDFGenerator:
    def __init__(self, style: Optional[PDFReportStyle] = None):
        self.style = style or PDFReportStyle()
        self._register_fonts()
        self.styles = self._build_styles()
        self._toc = None

    class _TOCDocTemplate(SimpleDocTemplate):
        def afterFlowable(self, flowable):
            try:
                from reportlab.platypus import Paragraph
                if isinstance(flowable, Paragraph):
                    style_name = getattr(flowable.style, 'name', '')
                    if style_name in ("Heading1", "Heading2"):
                        level = 0 if style_name == "Heading1" else 1
                        text = flowable.getPlainText()
                        self.notify('TOCEntry', (level, text, self.page))
            except Exception:
                # Gracefully ignore TOC collection errors
                pass

    def _register_fonts(self) -> None:
        try:
            if self.style.font_path:
                pdfmetrics.registerFont(TTFont(self.style.font_name, self.style.font_path))
                logger.info(f"注册TTF字体: {self.style.font_name}")
            else:
                pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
                self.style.font_name = "STSong-Light"
                logger.info("注册内置中文字体: STSong-Light")
        except Exception as e:
            logger.warning(f"字体注册失败，回退到Helvetica: {e}")
            self.style.font_name = "Helvetica"

    def _build_styles(self):
        base = getSampleStyleSheet()
        title = ParagraphStyle(
            name="Title",
            parent=base["Title"],
            fontName=self.style.font_name,
            fontSize=24,
            leading=28,
            textColor=self.style.primary_color,
            spaceAfter=18,
            alignment=1,
        )
        h1 = ParagraphStyle(
            name="Heading1",
            parent=base["Heading1"],
            fontName=self.style.font_name,
            fontSize=18,
            leading=22,
            textColor=self.style.primary_color,
            spaceBefore=12,
            spaceAfter=8,
        )
        h2 = ParagraphStyle(
            name="Heading2",
            parent=base["Heading2"],
            fontName=self.style.font_name,
            fontSize=14,
            leading=18,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=6,
        )
        body = ParagraphStyle(
            name="BodyText",
            parent=base["BodyText"],
            fontName=self.style.font_name,
            fontSize=11,
            leading=16,
        )
        meta = ParagraphStyle(
            name="Meta",
            parent=body,
            textColor=colors.HexColor("#555555"),
            fontSize=10,
        )
        return {
            "Title": title,
            "Heading1": h1,
            "Heading2": h2,
            "BodyText": body,
            "Meta": meta,
        }

    @staticmethod
    def _difficulty_name(level: DifficultyLevel) -> str:
        mapping = {
            DifficultyLevel.BEGINNER: "基础",
            DifficultyLevel.INTERMEDIATE: "中级",
            DifficultyLevel.ADVANCED: "高级",
        }
        return mapping.get(level, str(level.value))

    def _group_by_level(self, items: List[ClassifiedQuestion]) -> Dict[DifficultyLevel, List[ClassifiedQuestion]]:
        grouped: Dict[DifficultyLevel, List[ClassifiedQuestion]] = {
            DifficultyLevel.BEGINNER: [],
            DifficultyLevel.INTERMEDIATE: [],
            DifficultyLevel.ADVANCED: [],
        }
        for it in items:
            grouped[it.classification.level].append(it)
        return grouped

    @staticmethod
    def _esc(text: Optional[str]) -> str:
        if not text:
            return ""
        return html.escape(text).replace("\n", "<br/>")

    def _build_cover(self, doc_info: Dict[str, Any]) -> List[Any]:
        story: List[Any] = []
        story.append(Paragraph(self.style.title, self.styles["Title"]))
        subtitle = doc_info.get("subtitle") or "化学作业分层与难度分析报告"
        story.append(Paragraph(self._esc(subtitle), self.styles["Meta"]))
        # 说明页：排序依据
        sort_note = doc_info.get("sort_note")
        if sort_note:
            story.append(Spacer(1, 6))
            story.append(Paragraph(self._esc(sort_note), self.styles["Meta"]))
        story.append(Spacer(1, 18))

        meta_rows = [
            ["生成时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["作者", self.style.author],
            ["总题目数", str(doc_info.get("total_questions", "-"))],
        ]
        for k, v in doc_info.get("stats", {}).items():
            meta_rows.append([k, str(v)])

        table = Table(meta_rows, colWidths=[100, 380])
        table.setStyle(
            TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), self.style.font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f6f8fa")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(table)
        story.append(Spacer(1, 24))
        return story

    def _build_question_block(self, idx: int, item: ClassifiedQuestion) -> List[Any]:
        story: List[Any] = []
        title = f"题目 {idx}"
        story.append(Paragraph(title, self.styles["Heading2"]))

        story.append(Paragraph(self._esc(item.question_text), self.styles["BodyText"]))

        if item.answer_text:
            story.append(Spacer(1, 6))
            story.append(Paragraph("答案", self.styles["Meta"]))
            story.append(Paragraph(self._esc(item.answer_text), self.styles["BodyText"]))

        story.append(Spacer(1, 6))
        conf_txt = f"分类级别: {self._difficulty_name(item.classification.level)} / 置信度: {item.classification.confidence:.2f}"
        story.append(Paragraph(conf_txt, self.styles["Meta"]))

        # 元数据展示（题目ID、知识点标签等）
        meta_rows = []
        if item.metadata:
            qid = item.metadata.get("question_id")
            if qid:
                meta_rows.append(["题目ID", self._esc(str(qid))])
            tags = item.metadata.get("knowledge_tags")
            if tags:
                meta_rows.append(["知识点标签", self._esc(", ".join(map(str, tags)))])
            # 其他元数据通用展示
            for k, v in item.metadata.items():
                if k in ("question_id", "knowledge_tags"):
                    continue
                meta_rows.append([self._esc(str(k)), self._esc(str(v))])
        if meta_rows:
            table = Table(meta_rows, colWidths=[120, 360])
            table.setStyle(
                TableStyle([
                    ("FONTNAME", (0, 0), (-1, -1), self.style.font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fafbfc")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ])
            )
            story.append(Spacer(1, 6))
            story.append(table)

        if item.classification.reasons:
            lst = ListFlowable(
                [ListItem(Paragraph(self._esc(r), self.styles["BodyText"])) for r in item.classification.reasons],
                bulletType="bullet",
            )
            story.append(lst)

        if item.classification.detailed_analysis:
            rows = []
            for k, v in item.classification.detailed_analysis.items():
                rows.append([self._esc(str(k)), self._esc(str(v))])
            if rows:
                table = Table(rows, colWidths=[120, 360])
                table.setStyle(
                    TableStyle([
                        ("FONTNAME", (0, 0), (-1, -1), self.style.font_name),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fafbfc")),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ])
                )
                story.append(Spacer(1, 6))
                story.append(table)

        if item.classification.recommendations:
            story.append(Spacer(1, 6))
            story.append(Paragraph("建议", self.styles["Meta"]))
            lst = ListFlowable(
                [ListItem(Paragraph(self._esc(r), self.styles["BodyText"])) for r in item.classification.recommendations],
                bulletType="bullet",
            )
            story.append(lst)

        story.append(Spacer(1, 12))
        return story

    def generate_report(
        self,
        output_path: str,
        items: List[ClassifiedQuestion],
        metadata: Optional[Dict[str, Any]] = None,
        section_order: Optional[List[DifficultyLevel]] = None,
    ) -> str:
        section_order = section_order or [
            DifficultyLevel.BEGINNER,
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.ADVANCED,
        ]

        grouped = self._group_by_level(items)
        total = sum(len(v) for v in grouped.values())

        stats = {
            "基础题目": len(grouped[DifficultyLevel.BEGINNER]),
            "中级题目": len(grouped[DifficultyLevel.INTERMEDIATE]),
            "高级题目": len(grouped[DifficultyLevel.ADVANCED]),
        }

        doc = self._TOCDocTemplate(
            output_path,
            pagesize=self.style.page_size,
            leftMargin=self.style.margin_left,
            rightMargin=self.style.margin_right,
            topMargin=self.style.margin_top,
            bottomMargin=self.style.margin_bottom,
            title=self.style.title,
            author=self.style.author,
        )

        story: List[Any] = []
        story.extend(self._build_cover({
            "subtitle": metadata.get("subtitle") if metadata else None,
            "total_questions": total,
            "stats": stats,
            "sort_note": metadata.get("sort_note") if metadata else None,
        }))
        # 目录
        story.append(Paragraph("目录", self.styles["Heading1"]))
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(
                name="TOCHeading1",
                parent=self.styles["BodyText"],
                fontName=self.style.font_name,
                fontSize=11,
                leftIndent=16,
                firstLineIndent=-8,
                spaceBefore=4,
                leading=14,
            ),
            ParagraphStyle(
                name="TOCHeading2",
                parent=self.styles["BodyText"],
                fontName=self.style.font_name,
                fontSize=10,
                leftIndent=28,
                firstLineIndent=-12,
                spaceBefore=2,
                leading=12,
            ),
        ]
        story.append(toc)
        story.append(PageBreak())

        for level in section_order:
            section_items = grouped.get(level, [])
            if not section_items:
                continue

            header = f"{self._difficulty_name(level)}层次题目（{len(section_items)}题）"
            story.append(Paragraph(header, self.styles["Heading1"]))
            story.append(Spacer(1, 6))

            for idx, item in enumerate(section_items, start=1):
                story.extend(self._build_question_block(idx, item))

            story.append(PageBreak())

        doc.build(story)

        logger.info(f"分层PDF报告已生成: {output_path}")
        return output_path

    @staticmethod
    def _score(item: ClassifiedQuestion) -> float:
        try:
            return float(item.classification.detailed_analysis.get('total_score', 0))
        except Exception:
            return 0.0

    def generate_sorted_report(
        self,
        output_path: str,
        items: List[ClassifiedQuestion],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        # 稳定排序，按综合难度分数降序；可选保留组逻辑（group_id）
        def group_key(it: ClassifiedQuestion):
            gid = None
            if it.metadata:
                gid = it.metadata.get('group_id')
            return gid

        # 按组聚合，如果没有组ID则每题单独作为组
        groups: Dict[Any, List[ClassifiedQuestion]] = {}
        for idx, it in enumerate(items):
            gid = group_key(it)
            key = gid if gid is not None else f"__single__{idx}"
            groups.setdefault(key, []).append(it)

        # 组内保留原序，组间按组最大分数降序
        sorted_groups = sorted(
            groups.items(),
            key=lambda kv: max(self._score(x) for x in kv[1]),
            reverse=True,
        )
        sorted_items: List[ClassifiedQuestion] = []
        for _, g in sorted_groups:
            sorted_items.extend(sorted(g, key=lambda x: self._score(x), reverse=True))

        # 统计
        scores = [self._score(it) for it in sorted_items]
        total = len(sorted_items)
        stats = {
            "题目总数": total,
            "最高分": f"{max(scores) if scores else 0:.1f}",
            "最低分": f"{min(scores) if scores else 0:.1f}",
            "平均分": f"{(sum(scores)/total) if total else 0:.1f}",
        }

        # 文档
        doc = self._TOCDocTemplate(
            output_path,
            pagesize=self.style.page_size,
            leftMargin=self.style.margin_left,
            rightMargin=self.style.margin_right,
            topMargin=self.style.margin_top,
            bottomMargin=self.style.margin_bottom,
            title=self.style.title,
            author=self.style.author,
        )

        story: List[Any] = []
        story.extend(self._build_cover({
            "subtitle": metadata.get("subtitle") if metadata else None,
            "total_questions": total,
            "stats": stats,
            "sort_note": "排序依据：综合难度评分降序",
        }))
        # 目录
        story.append(Paragraph("目录", self.styles["Heading1"]))
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(
                name="TOCHeading1",
                parent=self.styles["BodyText"],
                fontName=self.style.font_name,
                fontSize=11,
                leftIndent=16,
                firstLineIndent=-8,
                spaceBefore=4,
                leading=14,
            ),
            ParagraphStyle(
                name="TOCHeading2",
                parent=self.styles["BodyText"],
                fontName=self.style.font_name,
                fontSize=10,
                leftIndent=28,
                firstLineIndent=-12,
                spaceBefore=2,
                leading=12,
            ),
        ]
        story.append(toc)
        story.append(PageBreak())

        # 正文标题
        header = f"题目列表（按综合难度评分降序，共{total}题）"
        story.append(Paragraph(header, self.styles["Heading1"]))
        story.append(Spacer(1, 6))

        for idx, item in enumerate(sorted_items, start=1):
            story.extend(self._build_question_block(idx, item))

        doc.build(story)
        logger.info(f"按难度分数降序PDF报告已生成: {output_path}")
        return output_path


def create_pdf(output_path: str, items: List[ClassifiedQuestion], metadata: Optional[Dict[str, Any]] = None) -> str:
    gen = ClassifiedPDFGenerator()
    return gen.generate_report(output_path, items, metadata)

def create_pdf_sorted(output_path: str, items: List[ClassifiedQuestion], metadata: Optional[Dict[str, Any]] = None) -> str:
    gen = ClassifiedPDFGenerator()
    return gen.generate_sorted_report(output_path, items, metadata)