"""
PDF文本提取器模块
负责从PDF文件中提取文本内容，支持批量处理和格式保持
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
import PyPDF2
import pdfplumber
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFTextExtractor:
    """PDF文本提取器类"""
    
    def __init__(self, preserve_layout: bool = True):
        """
        初始化PDF文本提取器
        
        Args:
            preserve_layout: 是否保持原始布局格式
        """
        self.preserve_layout = preserve_layout
        self.supported_formats = ['.pdf']
        
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """
        从单个PDF文件中提取文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            包含提取文本和元信息的字典
            {
                'text': str,           # 提取的文本内容
                'pages': int,          # 页数
                'file_path': str,      # 文件路径
                'metadata': dict,      # PDF元数据
                'extract_method': str, # 使用的提取方法
                'quality_score': float # 提取质量评分
            }
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
                
            logger.info(f"开始提取PDF文本: {pdf_path}")
            
            # 尝试使用pdfplumber提取（更好的格式保持）
            result = self._extract_with_pdfplumber(pdf_path)
            
            if not result['text'].strip():
                # 如果pdfplumber提取失败，尝试PyPDF2
                logger.warning("pdfplumber提取失败，尝试PyPDF2")
                result = self._extract_with_pypdf2(pdf_path)
                
            # 验证提取结果
            result['quality_score'] = self._assess_extraction_quality(result)
            
            logger.info(f"PDF文本提取完成: {pdf_path}, 页数: {result['pages']}, 质量评分: {result['quality_score']}")
            
            return result
            
        except Exception as e:
            logger.error(f"PDF文本提取失败 {pdf_path}: {str(e)}")
            return {
                'text': '',
                'pages': 0,
                'file_path': pdf_path,
                'metadata': {},
                'extract_method': 'failed',
                'quality_score': 0.0,
                'error': str(e)
            }
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, any]:
        """使用pdfplumber提取文本"""
        text_content = ""
        metadata = {}
        total_pages = 0
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                metadata = pdf.metadata or {}
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        if self.preserve_layout:
                            text_content += f"\n--- 第{i+1}页 ---\n"
                        text_content += page_text + "\n"
                        
                return {
                    'text': text_content.strip(),
                    'pages': total_pages,
                    'file_path': pdf_path,
                    'metadata': metadata,
                    'extract_method': 'pdfplumber',
                    'quality_score': 1.0 if text_content.strip() else 0.0
                }
                
        except Exception as e:
            logger.error(f"pdfplumber提取失败: {str(e)}")
            return {
                'text': '',
                'pages': 0,
                'file_path': pdf_path,
                'metadata': {},
                'extract_method': 'pdfplumber_failed',
                'quality_score': 0.0
            }
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Dict[str, any]:
        """使用PyPDF2提取文本"""
        text_content = ""
        metadata = {}
        total_pages = 0
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # 获取元数据
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    }
                
                # 提取每页文本
                for i, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            if self.preserve_layout:
                                text_content += f"\n--- 第{i+1}页 ---\n"
                            text_content += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"提取第{i+1}页失败: {str(e)}")
                        continue
                        
                return {
                    'text': text_content.strip(),
                    'pages': total_pages,
                    'file_path': pdf_path,
                    'metadata': metadata,
                    'extract_method': 'pypdf2',
                    'quality_score': 0.8 if text_content.strip() else 0.0
                }
                
        except Exception as e:
            logger.error(f"PyPDF2提取失败: {str(e)}")
            return {
                'text': '',
                'pages': 0,
                'file_path': pdf_path,
                'metadata': {},
                'extract_method': 'pypdf2_failed',
                'quality_score': 0.0
            }
    
    def _assess_extraction_quality(self, extraction_result: Dict[str, any]) -> float:
        """
        评估文本提取质量
        
        Args:
            extraction_result: 提取结果字典
            
        Returns:
            质量评分 (0.0-1.0)
        """
        text = extraction_result.get('text', '')
        
        if not text.strip():
            return 0.0
            
        # 基础质量评估
        quality_factors = []
        
        # 1. 文本长度因子
        text_length = len(text)
        if text_length > 1000:
            quality_factors.append(1.0)
        elif text_length > 500:
            quality_factors.append(0.8)
        elif text_length > 100:
            quality_factors.append(0.6)
        else:
            quality_factors.append(0.3)
        
        # 2. 可读性因子（检查中文字符比例）
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        if len(text) > 0:
            chinese_ratio = chinese_chars / len(text)
            if chinese_ratio > 0.3:  # 合理的中文字符比例
                quality_factors.append(1.0)
            elif chinese_ratio > 0.1:
                quality_factors.append(0.7)
            else:
                quality_factors.append(0.4)
        
        # 3. 格式完整性因子
        if extraction_result.get('pages', 0) > 0:
            quality_factors.append(0.9)
        else:
            quality_factors.append(0.3)
        
        # 4. 提取方法因子
        method = extraction_result.get('extract_method', '')
        if 'pdfplumber' in method and 'failed' not in method:
            quality_factors.append(1.0)
        elif 'pypdf2' in method and 'failed' not in method:
            quality_factors.append(0.8)
        else:
            quality_factors.append(0.2)
        
        # 计算平均质量评分
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
    
    def extract_from_directory(self, directory_path: str, recursive: bool = True) -> List[Dict[str, any]]:
        """
        从目录中提取所有PDF文件的文本
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归搜索子目录
            
        Returns:
            提取结果列表
        """
        results = []
        
        try:
            directory = Path(directory_path)
            
            if not directory.exists():
                logger.error(f"目录不存在: {directory_path}")
                return results
            
            # 搜索PDF文件
            if recursive:
                pdf_files = list(directory.rglob("*.pdf"))
            else:
                pdf_files = list(directory.glob("*.pdf"))
            
            logger.info(f"找到 {len(pdf_files)} 个PDF文件")
            
            for pdf_file in pdf_files:
                try:
                    result = self.extract_text_from_pdf(str(pdf_file))
                    results.append(result)
                except Exception as e:
                    logger.error(f"处理文件失败 {pdf_file}: {str(e)}")
                    results.append({
                        'text': '',
                        'pages': 0,
                        'file_path': str(pdf_file),
                        'metadata': {},
                        'extract_method': 'failed',
                        'quality_score': 0.0,
                        'error': str(e)
                    })
            
            logger.info(f"批量提取完成，成功处理 {len(results)} 个文件")
            
        except Exception as e:
            logger.error(f"批量提取失败: {str(e)}")
            
        return results
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return self.supported_formats.copy()
    
    def validate_pdf_file(self, pdf_path: str) -> Tuple[bool, str]:
        """
        验证PDF文件是否有效
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            if not os.path.exists(pdf_path):
                return False, "文件不存在"
            
            if not pdf_path.lower().endswith('.pdf'):
                return False, "不是PDF文件"
            
            # 尝试打开PDF文件
            with open(pdf_path, 'rb') as file:
                try:
                    PyPDF2.PdfReader(file)
                    return True, ""
                except Exception as e:
                    return False, f"PDF文件损坏: {str(e)}"
                    
        except Exception as e:
            return False, f"验证失败: {str(e)}"