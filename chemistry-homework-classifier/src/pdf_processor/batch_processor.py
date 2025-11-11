"""
批量PDF处理器模块
负责批量处理多个PDF文件，提供进度跟踪和错误处理
"""

import os
import logging
from typing import List, Dict, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .extractor import PDFTextExtractor
from .parser import QuestionAnswerParser
from .validator import PDFValidator

logger = logging.getLogger(__name__)


class BatchProcessor:
    """批量PDF处理器类"""
    
    def __init__(self, max_workers: int = 4, progress_callback: Optional[Callable] = None):
        """
        初始化批量处理器
        
        Args:
            max_workers: 最大并发工作线程数
            progress_callback: 进度回调函数
        """
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.text_extractor = PDFTextExtractor()
        self.question_parser = QuestionAnswerParser()
        self.pdf_validator = PDFValidator()
        
        # 统计信息
        self.processing_stats = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'total_questions': 0,
            'processing_time': 0.0
        }
    
    def process_batch(self, input_paths: List[str], output_dir: str, 
                     preserve_structure: bool = True) -> Dict[str, any]:
        """
        批量处理PDF文件
        
        Args:
            input_paths: PDF文件路径列表
            output_dir: 输出目录
            preserve_structure: 是否保持原始目录结构
            
        Returns:
            处理结果字典
        """
        start_time = time.time()
        
        logger.info(f"开始批量处理 {len(input_paths)} 个PDF文件")
        
        # 重置统计信息
        self.processing_stats = {
            'total_files': len(input_paths),
            'successful_files': 0,
            'failed_files': 0,
            'total_questions': 0,
            'processing_time': 0.0
        }
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 处理文件
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            future_to_path = {
                executor.submit(self._process_single_file, path, output_dir, preserve_structure): path
                for path in input_paths
            }
            
            # 收集结果
            for i, future in enumerate(as_completed(future_to_path), 1):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 更新统计信息
                    if result.get('success', False):
                        self.processing_stats['successful_files'] += 1
                        self.processing_stats['total_questions'] += len(result.get('questions', []))
                    else:
                        self.processing_stats['failed_files'] += 1
                    
                    # 进度回调
                    if self.progress_callback:
                        progress = {
                            'current': i,
                            'total': len(input_paths),
                            'percentage': (i / len(input_paths)) * 100,
                            'current_file': path,
                            'success': result.get('success', False)
                        }
                        self.progress_callback(progress)
                        
                except Exception as e:
                    logger.error(f"处理文件 {path} 时发生异常: {str(e)}")
                    self.processing_stats['failed_files'] += 1
                    results.append({
                        'file_path': path,
                        'success': False,
                        'error': str(e),
                        'questions': []
                    })
        
        # 计算总处理时间
        end_time = time.time()
        self.processing_stats['processing_time'] = end_time - start_time
        
        logger.info(f"批量处理完成，耗时: {self.processing_stats['processing_time']:.2f}秒")
        
        return {
            'results': results,
            'statistics': self.processing_stats,
            'success_rate': self.processing_stats['successful_files'] / len(input_paths) if input_paths else 0
        }
    
    def _process_single_file(self, pdf_path: str, output_dir: str, 
                           preserve_structure: bool) -> Dict[str, any]:
        """
        处理单个PDF文件
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            preserve_structure: 是否保持原始目录结构
            
        Returns:
            处理结果字典
        """
        logger.info(f"开始处理文件: {pdf_path}")
        
        try:
            # 验证PDF文件
            is_valid, error_msg = self.pdf_validator.validate_pdf(pdf_path)
            if not is_valid:
                return {
                    'file_path': pdf_path,
                    'success': False,
                    'error': f"PDF验证失败: {error_msg}",
                    'questions': []
                }
            
            # 提取文本
            extraction_result = self.text_extractor.extract_text_from_pdf(pdf_path)
            
            if not extraction_result['text'] or extraction_result['quality_score'] < 0.5:
                return {
                    'file_path': pdf_path,
                    'success': False,
                    'error': "文本提取质量过低",
                    'questions': []
                }
            
            # 解析题目
            questions = self.question_parser.parse_questions_and_answers(extraction_result['text'])
            
            if not questions:
                return {
                    'file_path': pdf_path,
                    'success': False,
                    'error': "未找到任何题目",
                    'questions': []
                }
            
            # 生成输出文件路径
            output_subdir = self._get_output_subdirectory(pdf_path, output_dir, preserve_structure)
            os.makedirs(output_subdir, exist_ok=True)
            
            # 准备结果数据
            result = {
                'file_path': pdf_path,
                'success': True,
                'extraction_result': extraction_result,
                'questions': questions,
                'output_directory': output_subdir,
                'question_statistics': self.question_parser.get_question_statistics(questions)
            }
            
            logger.info(f"文件处理成功: {pdf_path}, 找到 {len(questions)} 个题目")
            
            return result
            
        except Exception as e:
            logger.error(f"处理文件 {pdf_path} 失败: {str(e)}")
            return {
                'file_path': pdf_path,
                'success': False,
                'error': str(e),
                'questions': []
            }
    
    def _get_output_subdirectory(self, input_path: str, output_dir: str, 
                               preserve_structure: bool) -> str:
        """
        获取输出子目录路径
        
        Args:
            input_path: 输入文件路径
            output_dir: 输出根目录
            preserve_structure: 是否保持原始结构
            
        Returns:
            输出子目录路径
        """
        if not preserve_structure:
            return output_dir
        
        # 获取输入文件的相对目录结构
        input_path_obj = Path(input_path)
        
        # 如果输入文件在子目录中，保持相对结构
        if len(input_path_obj.parts) > 1:
            relative_dir = input_path_obj.parent.name
            return os.path.join(output_dir, relative_dir)
        
        return output_dir
    
    def process_directory(self, input_dir: str, output_dir: str, 
                         recursive: bool = True, preserve_structure: bool = True) -> Dict[str, any]:
        """
        处理整个目录的PDF文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            recursive: 是否递归处理子目录
            preserve_structure: 是否保持原始目录结构
            
        Returns:
            处理结果字典
        """
        logger.info(f"开始处理目录: {input_dir}")
        
        # 查找PDF文件
        input_path_obj = Path(input_dir)
        
        if recursive:
            pdf_files = list(input_path_obj.rglob("*.pdf"))
        else:
            pdf_files = list(input_path_obj.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"在目录 {input_dir} 中未找到PDF文件")
            return {
                'results': [],
                'statistics': self.processing_stats,
                'success_rate': 0
            }
        
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 转换为字符串路径列表
        pdf_paths = [str(file) for file in pdf_files]
        
        # 批量处理
        return self.process_batch(pdf_paths, output_dir, preserve_structure)
    
    def get_processing_statistics(self) -> Dict[str, any]:
        """获取处理统计信息"""
        return self.processing_stats.copy()
    
    def reset_statistics(self):
        """重置统计信息"""
        self.processing_stats = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'total_questions': 0,
            'processing_time': 0.0
        }
    
    def validate_batch_input(self, input_paths: List[str]) -> Dict[str, List[str]]:
        """
        验证批量输入文件
        
        Args:
            input_paths: 输入文件路径列表
            
        Returns:
            验证结果字典
        """
        valid_files = []
        invalid_files = []
        
        for path in input_paths:
            is_valid, error_msg = self.pdf_validator.validate_pdf(path)
            if is_valid:
                valid_files.append(path)
            else:
                invalid_files.append({
                    'path': path,
                    'error': error_msg
                })
        
        return {
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'validation_rate': len(valid_files) / len(input_paths) if input_paths else 0
        }
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return self.text_extractor.get_supported_formats()


class ProcessingProgressTracker:
    """处理进度跟踪器"""
    
    def __init__(self):
        self.total_files = 0
        self.processed_files = 0
        self.current_file = ""
        self.start_time = None
        self.errors = []
        
    def start_processing(self, total_files: int):
        """开始处理"""
        self.total_files = total_files
        self.processed_files = 0
        self.start_time = time.time()
        self.errors = []
        
    def update_progress(self, current_file: str, success: bool, error: Optional[str] = None):
        """更新进度"""
        self.processed_files += 1
        self.current_file = current_file
        
        if not success and error:
            self.errors.append({
                'file': current_file,
                'error': error,
                'timestamp': time.time()
            })
    
    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    def get_elapsed_time(self) -> float:
        """获取已用时间"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def get_estimated_remaining_time(self) -> float:
        """获取预计剩余时间"""
        if self.processed_files == 0 or self.total_files == 0:
            return 0.0
        
        elapsed_time = self.get_elapsed_time()
        avg_time_per_file = elapsed_time / self.processed_files
        remaining_files = self.total_files - self.processed_files
        
        return avg_time_per_file * remaining_files
    
    def get_summary(self) -> Dict[str, any]:
        """获取处理摘要"""
        return {
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'progress_percentage': self.get_progress_percentage(),
            'elapsed_time': self.get_elapsed_time(),
            'estimated_remaining_time': self.get_estimated_remaining_time(),
            'error_count': len(self.errors),
            'current_file': self.current_file
        }