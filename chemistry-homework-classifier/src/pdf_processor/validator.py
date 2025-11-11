"""
PDF验证器模块
负责验证PDF文件的有效性和完整性
"""

import os
import logging
from typing import Tuple, List, Dict
import PyPDF2
import pdfplumber
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFValidator:
    """PDF文件验证器类"""
    
    def __init__(self):
        """初始化验证器"""
        self.supported_formats = ['.pdf']
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.max_pages = 1000  # 最大页数限制
    
    def validate_pdf(self, pdf_path: str) -> Tuple[bool, str]:
        """
        验证PDF文件
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            # 基本文件验证
            is_valid, error_msg = self._validate_basic_file(pdf_path)
            if not is_valid:
                return False, error_msg
            
            # PDF格式验证
            is_valid, error_msg = self._validate_pdf_format(pdf_path)
            if not is_valid:
                return False, error_msg
            
            # 内容完整性验证
            is_valid, error_msg = self._validate_pdf_content(pdf_path)
            if not is_valid:
                return False, error_msg
            
            logger.info(f"PDF文件验证通过: {pdf_path}")
            return True, ""
            
        except Exception as e:
            logger.error(f"PDF验证异常 {pdf_path}: {str(e)}")
            return False, f"验证异常: {str(e)}"
    
    def _validate_basic_file(self, file_path: str) -> Tuple[bool, str]:
        """
        基本文件验证
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False, "文件不存在"
        
        # 检查是否是文件
        if not os.path.isfile(file_path):
            return False, "路径不是文件"
        
        # 检查文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            return False, f"不支持的文件格式: {file_ext}"
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "文件为空"
        
        if file_size > self.max_file_size:
            return False, f"文件过大: {file_size / (1024*1024):.1f}MB > {self.max_file_size / (1024*1024):.1f}MB"
        
        return True, ""
    
    def _validate_pdf_format(self, pdf_path: str) -> Tuple[bool, str]:
        """
        验证PDF格式
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            # 尝试用PyPDF2打开
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 检查页数
                num_pages = len(pdf_reader.pages)
                if num_pages == 0:
                    return False, "PDF文件没有页面"
                
                if num_pages > self.max_pages:
                    return False, f"页数过多: {num_pages} > {self.max_pages}"
                
                # 检查PDF版本
                if pdf_reader.metadata:
                    pdf_version = pdf_reader.metadata.get('/Version', 'Unknown')
                    logger.debug(f"PDF版本: {pdf_version}")
                
                return True, ""
                
        except PyPDF2.errors.PdfReadError as e:
            return False, f"PDF格式错误: {str(e)}"
        except Exception as e:
            return False, f"PDF格式验证失败: {str(e)}"
    
    def _validate_pdf_content(self, pdf_path: str) -> Tuple[bool, str]:
        """
        验证PDF内容完整性
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            # 尝试提取第一页文本验证内容完整性
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF没有可读取的页面"
                
                # 尝试读取第一页
                first_page = pdf.pages[0]
                try:
                    # 尝试提取文本（不实际获取内容，只验证可读性）
                    first_page.extract_text()
                except Exception as e:
                    return False, f"PDF内容不可读: {str(e)}"
                
                # 检查加密状态
                if pdf.encrypted:
                    return False, "PDF文件已加密"
                
                return True, ""
                
        except Exception as e:
            return False, f"PDF内容验证失败: {str(e)}"
    
    def validate_batch(self, file_paths: List[str]) -> Dict[str, any]:
        """
        批量验证PDF文件
        
        Args:
            file_paths: PDF文件路径列表
            
        Returns:
            验证结果字典
        """
        results = {
            'valid_files': [],
            'invalid_files': [],
            'total_files': len(file_paths),
            'validation_summary': {}
        }
        
        for file_path in file_paths:
            is_valid, error_msg = self.validate_pdf(file_path)
            
            if is_valid:
                results['valid_files'].append(file_path)
            else:
                results['invalid_files'].append({
                    'file_path': file_path,
                    'error': error_msg
                })
        
        # 生成验证摘要
        valid_count = len(results['valid_files'])
        invalid_count = len(results['invalid_files'])
        
        results['validation_summary'] = {
            'total_files': len(file_paths),
            'valid_files': valid_count,
            'invalid_files': invalid_count,
            'validity_rate': valid_count / len(file_paths) if file_paths else 0,
            'common_errors': self._analyze_common_errors(results['invalid_files'])
        }
        
        return results
    
    def _analyze_common_errors(self, invalid_files: List[Dict[str, str]]) -> Dict[str, int]:
        """
        分析常见错误
        
        Args:
            invalid_files: 无效文件列表
            
        Returns:
            错误统计字典
        """
        error_counts = {}
        
        for invalid_file in invalid_files:
            error = invalid_file['error']
            error_counts[error] = error_counts.get(error, 0) + 1
        
        return error_counts
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, any]:
        """
        获取PDF文件详细信息
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            PDF信息字典
        """
        try:
            info = {
                'file_path': pdf_path,
                'file_size': os.path.getsize(pdf_path),
                'is_valid': False,
                'error': "",
                'metadata': {},
                'page_count': 0,
                'is_encrypted': False,
                'pdf_version': 'Unknown'
            }
            
            # 基本验证
            is_valid, error_msg = self._validate_basic_file(pdf_path)
            if not is_valid:
                info['error'] = error_msg
                return info
            
            # 获取详细信息
            with open(pdf_path, 'rb') as file:
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    # 页数
                    info['page_count'] = len(pdf_reader.pages)
                    
                    # 元数据
                    if pdf_reader.metadata:
                        info['metadata'] = {
                            'title': pdf_reader.metadata.get('/Title', ''),
                            'author': pdf_reader.metadata.get('/Author', ''),
                            'subject': pdf_reader.metadata.get('/Subject', ''),
                            'creator': pdf_reader.metadata.get('/Creator', ''),
                            'producer': pdf_reader.metadata.get('/Producer', ''),
                            'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                            'modification_date': str(pdf_reader.metadata.get('/ModDate', ''))
                        }
                    
                    # 加密状态
                    info['is_encrypted'] = pdf_reader.is_encrypted
                    
                    # PDF版本
                    info['pdf_version'] = pdf_reader.pdf_header_version if hasattr(pdf_reader, 'pdf_header_version') else 'Unknown'
                    
                    info['is_valid'] = True
                    
                except Exception as e:
                    info['error'] = f"无法读取PDF信息: {str(e)}"
                    
        except Exception as e:
            info['error'] = f"获取PDF信息失败: {str(e)}"
        
        return info
    
    def check_pdf_quality(self, pdf_path: str) -> Dict[str, any]:
        """
        检查PDF质量
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            质量检查结果字典
        """
        quality_info = {
            'file_path': pdf_path,
            'overall_quality': 'unknown',
            'quality_score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # 基本验证
            is_valid, error_msg = self.validate_pdf(pdf_path)
            if not is_valid:
                quality_info['issues'].append(error_msg)
                quality_info['overall_quality'] = 'poor'
                return quality_info
            
            # 获取PDF信息
            pdf_info = self.get_pdf_info(pdf_path)
            
            # 评估质量
            quality_score = 1.0
            
            # 页数评估
            page_count = pdf_info['page_count']
            if page_count < 1:
                quality_info['issues'].append("PDF没有内容页面")
                quality_score -= 0.5
            elif page_count > 50:
                quality_info['issues'].append("PDF页数过多，可能影响处理性能")
                quality_score -= 0.1
            
            # 文件大小评估
            file_size_mb = pdf_info['file_size'] / (1024 * 1024)
            if file_size_mb > 50:
                quality_info['issues'].append("PDF文件过大")
                quality_score -= 0.2
            elif file_size_mb < 0.1:
                quality_info['issues'].append("PDF文件过小，可能内容不完整")
                quality_score -= 0.1
            
            # 元数据评估
            metadata = pdf_info['metadata']
            if not metadata.get('title') and not metadata.get('subject'):
                quality_info['recommendations'].append("建议添加PDF标题和主题信息")
                quality_score -= 0.05
            
            # 加密评估
            if pdf_info['is_encrypted']:
                quality_info['issues'].append("PDF已加密，需要解密才能处理")
                quality_score -= 0.3
            
            # 设置质量等级
            if quality_score >= 0.9:
                quality_info['overall_quality'] = 'excellent'
            elif quality_score >= 0.8:
                quality_info['overall_quality'] = 'good'
            elif quality_score >= 0.6:
                quality_info['overall_quality'] = 'fair'
            else:
                quality_info['overall_quality'] = 'poor'
            
            quality_info['quality_score'] = max(0.0, quality_score)
            
        except Exception as e:
            quality_info['issues'].append(f"质量检查失败: {str(e)}")
            quality_info['overall_quality'] = 'unknown'
        
        return quality_info
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return self.supported_formats.copy()
    
    def set_max_file_size(self, size_mb: int):
        """设置最大文件大小限制（MB）"""
        self.max_file_size = size_mb * 1024 * 1024
    
    def set_max_pages(self, max_pages: int):
        """设置最大页数限制"""
        self.max_pages = max_pages