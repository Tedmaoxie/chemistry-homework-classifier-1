"""
题目和答案解析器模块
负责从提取的文本中识别和分离化学题目及答案
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChemistryQuestion:
    """化学题目数据结构"""
    question_id: str
    question_text: str
    answer_text: Optional[str] = None
    question_type: str = "unknown"  # choice, fill_blank, calculation, theory, experiment
    difficulty_score: float = 0.0
    page_number: int = 0
    original_format: str = ""
    

class QuestionAnswerParser:
    """题目答案解析器类"""
    
    def __init__(self):
        """初始化解析器"""
        # 定义题目编号模式
        self.question_patterns = [
            r'^(\d+)\s*[\.、]\s*(.+?)(?=\n\d+\s*[\.、]|\n答案[:：]|\n答[:：]|$)',  # 1. 题目内容
            r'^【(\d+)】\s*(.+?)(?=\n【\d+】|\n答案[:：]|\n答[:：]|$)',  # 【1】题目内容
            r'^(\d+)\.\s*(.+?)(?=\n\d+\.\s|\n答案[:：]|\n答[:：]|$)',  # 1. 题目内容（英文句点）
            r'^第?([一二三四五六七八九十]+)[题题号]\s*[\.、]?\s*(.+?)(?=\n第?[一二三四五六七八九十]+[题题号]|\n答案[:：]|\n答[:：]|$)',  # 第一题 题目内容
        ]
        
        # 定义答案模式
        self.answer_patterns = [
            r'^答案[:：]\s*(.+?)(?=\n\d+\s*[\.、]|\n【\d+】|$)',  # 答案: 
            r'^答[:：]\s*(.+?)(?=\n\d+\s*[\.、]|\n【\d+】|$)',  # 答: 
            r'^(\d+)\s*答案?[:：]\s*(.+?)(?=\n\d+\s*答案?[:：]|$)',  # 1 答案: 
            r'^【(\d+)】\s*答案?[:：]\s*(.+?)(?=\n【\d+】\s*答案?[:：]|$)',  # 【1】 答案: 
        ]
        
        # 题目类型识别关键词
        self.question_type_keywords = {
            'choice': ['选择', '选项', 'A.', 'B.', 'C.', 'D.', 'E.'],
            'fill_blank': ['填空', '填写', '___', '……', '（ ）', '()', '空格'],
            'calculation': ['计算', '求解', '求', '算', '结果是', '等于'],
            'theory': ['解释', '说明', '阐述', '分析', '比较', '对比'],
            'experiment': ['实验', '操作', '步骤', '现象', '结论']
        }
        
        # 化学题目特定模式
        self.chemistry_patterns = {
            'equation': r'[A-Za-z0-9+\-→⇌=()]+',  # 化学方程式
            'element': r'[A-Z][a-z]?\d*',  # 元素符号
            'formula': r'[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*',  # 化学式
            'unit': r'(?:mol|g|L|mL|mol/L|g/mol|℃|K|Pa|kPa|atm)'  # 化学单位
        }
    
    def parse_questions_and_answers(self, text: str) -> List[ChemistryQuestion]:
        """
        从文本中解析题目和答案
        
        Args:
            text: 提取的PDF文本内容
            
        Returns:
            ChemistryQuestion对象列表
        """
        logger.info("开始解析题目和答案")
        
        if not text.strip():
            logger.warning("输入文本为空")
            return []
        
        # 预处理文本
        processed_text = self._preprocess_text(text)
        
        # 提取题目
        questions = self._extract_questions(processed_text)
        
        # 提取答案并匹配到题目
        questions_with_answers = self._extract_and_match_answers(processed_text, questions)
        
        # 识别题目类型
        for question in questions_with_answers:
            question.question_type = self._identify_question_type(question.question_text)
        
        logger.info(f"解析完成，共找到 {len(questions_with_answers)} 个题目")
        
        return questions_with_answers
    
    def _preprocess_text(self, text: str) -> str:
        """
        预处理文本，统一格式
        
        Args:
            text: 原始文本
            
        Returns:
            预处理后的文本
        """
        # 移除多余的空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 统一中英文标点
        text = text.replace('．', '.').replace('，', ',').replace('：', ':')
        
        # 移除页码标记
        text = re.sub(r'--- 第\d+页 ---', '', text)
        
        # 移除多余的空格
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()
    
    def _extract_questions(self, text: str) -> List[ChemistryQuestion]:
        """
        提取题目
        
        Args:
            text: 预处理后的文本
            
        Returns:
            题目列表
        """
        questions = []
        
        for pattern in self.question_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                try:
                    if len(match.groups()) == 2:
                        question_id = match.group(1).strip()
                        question_text = match.group(2).strip()
                    else:
                        question_id = str(len(questions) + 1)
                        question_text = match.group(0).strip()
                    
                    if question_text and len(question_text) > 10:  # 过滤过短的文本
                        question = ChemistryQuestion(
                            question_id=question_id,
                            question_text=question_text,
                            original_format=match.group(0)
                        )
                        questions.append(question)
                        
                except Exception as e:
                    logger.warning(f"解析题目失败: {str(e)}")
                    continue
        
        # 如果没有找到符合模式的题目，尝试智能分段
        if not questions:
            questions = self._smart_segment_questions(text)
        
        return questions
    
    def _smart_segment_questions(self, text: str) -> List[ChemistryQuestion]:
        """
        智能分段提取题目（当模式匹配失败时）
        
        Args:
            text: 文本内容
            
        Returns:
            题目列表
        """
        questions = []
        paragraphs = text.split('\n\n')
        
        current_question = ""
        question_counter = 1
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 检查是否是题目段落
            if self._is_question_paragraph(paragraph):
                if current_question:  # 保存前一个题目
                    question = ChemistryQuestion(
                        question_id=str(question_counter),
                        question_text=current_question.strip(),
                        original_format=current_question
                    )
                    questions.append(question)
                    question_counter += 1
                
                current_question = paragraph
            else:
                # 可能是题目的延续
                current_question += "\n" + paragraph
        
        # 保存最后一个题目
        if current_question and len(current_question.strip()) > 20:
            question = ChemistryQuestion(
                question_id=str(question_counter),
                question_text=current_question.strip(),
                original_format=current_question
            )
            questions.append(question)
        
        return questions
    
    def _is_question_paragraph(self, paragraph: str) -> bool:
        """
        判断段落是否是题目
        
        Args:
            paragraph: 段落文本
            
        Returns:
            是否是题目
        """
        # 检查是否包含题目特征
        indicators = [
            len(paragraph) > 20,  # 长度足够
            any(char.isdigit() for char in paragraph[:10]),  # 开头有数字
            '？' in paragraph or '?' in paragraph,  # 包含问号
            any(keyword in paragraph for keyword in ['计算', '求', '解释', '说明']),  # 包含动词
            self._contains_chemistry_content(paragraph)  # 包含化学内容
        ]
        
        return sum(indicators) >= 3
    
    def _contains_chemistry_content(self, text: str) -> bool:
        """
        检查文本是否包含化学相关内容
        
        Args:
            text: 文本内容
            
        Returns:
            是否包含化学内容
        """
        chemistry_indicators = [
            r'[A-Z][a-z]?\d*',  # 元素符号
            r'[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*',  # 化学式
            r'→|⇌|=',  # 反应箭头
            r'mol|g|L|mol/L|g/mol',  # 化学单位
            r'原子|分子|离子|化合物|元素|化学键'  # 化学术语
        ]
        
        for pattern in chemistry_indicators:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _extract_and_match_answers(self, text: str, questions: List[ChemistryQuestion]) -> List[ChemistryQuestion]:
        """
        提取答案并匹配到对应题目
        
        Args:
            text: 原始文本
            questions: 题目列表
            
        Returns:
            包含答案的题目列表
        """
        # 提取所有答案
        all_answers = []
        
        for pattern in self.answer_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                try:
                    if len(match.groups()) == 2:
                        answer_id = match.group(1).strip()
                        answer_text = match.group(2).strip()
                    else:
                        answer_id = ""
                        answer_text = match.group(1).strip()
                    
                    if answer_text:
                        all_answers.append({
                            'id': answer_id,
                            'text': answer_text,
                            'pattern': pattern
                        })
                except Exception as e:
                    logger.warning(f"解析答案失败: {str(e)}")
                    continue
        
        # 匹配答案到题目
        for question in questions:
            # 尝试按ID匹配
            if question.question_id:
                matching_answers = [ans for ans in all_answers if ans['id'] == question.question_id]
                if matching_answers:
                    question.answer_text = matching_answers[0]['text']
                    continue
            
            # 如果没有ID匹配，尝试按位置匹配（假设答案在题目之后）
            question_pos = text.find(question.original_format)
            if question_pos != -1:
                for answer in all_answers:
                    answer_pos = text.find(answer['text'])
                    if answer_pos > question_pos:
                        question.answer_text = answer['text']
                        break
        
        return questions
    
    def _identify_question_type(self, question_text: str) -> str:
        """
        识别题目类型
        
        Args:
            question_text: 题目文本
            
        Returns:
            题目类型
        """
        question_text_lower = question_text.lower()
        
        # 检查各种题目类型的关键词
        for q_type, keywords in self.question_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_text_lower)
            if score >= 2:  # 至少需要匹配2个关键词
                return q_type
        
        # 特殊检查选择题
        if re.search(r'[A-E]\s*[\.、)]', question_text):
            return 'choice'
        
        # 特殊检查填空题
        if re.search(r'_{3,}|\.{3,}|（\s*）|\(\s*\)', question_text):
            return 'fill_blank'
        
        # 特殊检查计算题
        if re.search(r'计算|求解|求\s*\w+|[\d\.]+\s*[×÷+\-]\s*[\d\.]+', question_text):
            return 'calculation'
        
        # 默认返回理论题
        return 'theory'
    
    def extract_chemical_formulas(self, text: str) -> List[str]:
        """
        提取文本中的化学式
        
        Args:
            text: 文本内容
            
        Returns:
            化学式列表
        """
        formula_pattern = self.chemistry_patterns['formula']
        formulas = re.findall(formula_pattern, text)
        return [formula for formula in formulas if len(formula) > 1]
    
    def extract_chemical_equations(self, text: str) -> List[str]:
        """
        提取文本中的化学方程式
        
        Args:
            text: 文本内容
            
        Returns:
            化学方程式列表
        """
        equation_pattern = r'[A-Za-z0-9+\-→⇌=()]+\s*[-→⇌=]\s*[A-Za-z0-9+\-→⇌=()]+'
        equations = re.findall(equation_pattern, text)
        return [eq for eq in equations if len(eq) > 5]
    
    def get_question_statistics(self, questions: List[ChemistryQuestion]) -> Dict[str, any]:
        """
        获取题目统计信息
        
        Args:
            questions: 题目列表
            
        Returns:
            统计信息字典
        """
        if not questions:
            return {}
        
        type_counts = {}
        for question in questions:
            q_type = question.question_type
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        total_questions = len(questions)
        questions_with_answers = sum(1 for q in questions if q.answer_text)
        
        return {
            'total_questions': total_questions,
            'questions_with_answers': questions_with_answers,
            'answer_coverage': questions_with_answers / total_questions if total_questions > 0 else 0,
            'type_distribution': type_counts,
            'average_question_length': sum(len(q.question_text) for q in questions) / total_questions,
            'longest_question': max(len(q.question_text) for q in questions),
            'shortest_question': min(len(q.question_text) for q in questions)
        }