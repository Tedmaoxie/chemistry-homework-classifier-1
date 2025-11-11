"""
多维度难度评估系统
综合分析题目的文本复杂度、概念深度、计算步骤等因素
"""

import logging
import re
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

from ..data.chemistry_vocab import ChemistryVocabulary, ChemistryConcepts

logger = logging.getLogger(__name__)


@dataclass
class DifficultyFeatures:
    """难度特征数据类"""
    # 基础特征
    text_length: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    
    # 词汇复杂度
    chemistry_vocab_ratio: float = 0.0
    avg_chemistry_complexity: float = 0.0
    max_chemistry_complexity: int = 0
    technical_terms_count: int = 0
    
    # 概念深度
    concept_count: int = 0
    avg_concept_level: float = 0.0
    max_concept_level: int = 0
    missing_prerequisites: int = 0
    
    # 计算复杂度
    calculation_steps: int = 0
    formula_count: int = 0
    numerical_values: int = 0
    units_count: int = 0
    
    # 结构复杂度
    question_parts: int = 1
    sub_questions: int = 1
    has_diagram: bool = False
    has_table: bool = False
    
    # 推理复杂度
    reasoning_steps: int = 0
    conditional_logic: bool = False
    multi_step_reasoning: bool = False
    abstract_thinking: bool = False

    # 章节标签（用于知识覆盖均衡）
    chapter_tags: List[str] = None
    primary_chapter: str = ""


class MultiDimensionalDifficultyAssessor:
    """多维度难度评估器"""
    
    def __init__(self, vocab_db: ChemistryVocabulary = None, concepts_db: ChemistryConcepts = None):
        """
        初始化评估器
        
        Args:
            vocab_db: 化学词汇数据库
            concepts_db: 化学概念数据库
        """
        self.vocab_db = vocab_db or ChemistryVocabulary()
        self.concepts_db = concepts_db or ChemistryConcepts()
        
        # 定义权重配置
        self.weights = {
            'text_complexity': 0.15,      # 文本复杂度
            'vocabulary_complexity': 0.20,  # 词汇复杂度
            'concept_depth': 0.25,        # 概念深度
            'calculation_complexity': 0.20, # 计算复杂度
            'structural_complexity': 0.10, # 结构复杂度
            'reasoning_complexity': 0.10   # 推理复杂度
        }
        
        # 难度级别阈值（按目标比例 60%/30%/10% 调整）
        # beginner: 0-60, intermediate: 60-90, advanced: 90-100
        self.difficulty_thresholds = {
            'beginner': {'min': 0, 'max': 60},
            'intermediate': {'min': 60, 'max': 90},
            'advanced': {'min': 90, 'max': 100}
        }
        
        # 化学计量关键词
        self.calculation_keywords = [
            '计算', '求', '解', '得出', '结果是', '等于', '为', '多少',
            '浓度', '质量', '体积', '摩尔', '物质的量', 'pH', '平衡常数',
            '速率常数', '活化能', '电极电势'
        ]
        
        # 推理关键词
        self.reasoning_keywords = [
            '解释', '说明', '原因', '为什么', '分析', '判断', '比较',
            '推导', '证明', '预测', '推断', '结论', '结论是什么'
        ]
        
        # 条件逻辑关键词
        self.conditional_keywords = [
            '如果', '假如', '当', '在...情况下', '条件下', '假设',
            '给定', '已知', '若', '则', '那么'
        ]
        
        # 高中化学章节关键词映射（用于范围限定与覆盖均衡）
        self.chapter_keywords = {
            '基础概念与结构': [
                '原子', '分子', '离子', '化学键', '共价键', '离子键', '金属键',
                '元素', '周期表', '元素周期律', '原子半径', '电子排布', '价电子'
            ],
            '反应原理': [
                '化学平衡', '勒夏特列', '反应速率', '速率常数', '活化能', '热化学', '热力学',
                '放热', '吸热', '焓', '熵', '吉布斯', '自发性'
            ],
            '酸碱与氧化还原': [
                '酸碱', '酸碱理论', '酸度', '碱度', 'pH', '缓冲溶液', '滴定',
                '氧化还原', '氧化剂', '还原剂', '电极电势', '半反应'
            ],
            '有机基础': [
                '有机化学', '官能团', '烷烃', '烯烃', '炔烃', '芳香族', '苯',
                '异构', '同分异构', '结构异构', '顺反异构', '取代反应', '加成反应'
            ],
            '实验与方法': [
                '实验', '测定', '测量', '设计', '方案', '步骤', '现象', '仪器', '误差', '操作'
            ]
        }
        
        logger.info("多维度难度评估器初始化完成")
    
    def assess_difficulty(self, question_text: str, answer_text: str = None) -> Dict[str, any]:
        """
        综合评估题目难度
        
        Args:
            question_text: 题目文本
            answer_text: 答案文本（可选）
            
        Returns:
            难度评估结果
        """
        try:
            # 提取特征
            features = self._extract_features(question_text, answer_text)
            
            # 计算各维度分数
            scores = self._calculate_dimension_scores(features)
            
            # 计算综合难度分数
            total_score = self._calculate_total_score(scores)
            
            # 确定难度级别
            difficulty_level = self._determine_difficulty_level(total_score)
            
            # 生成详细分析
            detailed_analysis = self._generate_detailed_analysis(features, scores, total_score)
            
            result = {
                'total_score': total_score,
                'difficulty_level': difficulty_level,
                'dimension_scores': scores,
                'features': self._features_to_dict(features),
                'detailed_analysis': detailed_analysis,
                'recommendations': self._generate_recommendations(features, total_score)
            }
            
            logger.info(f"难度评估完成: {difficulty_level} (分数: {total_score:.1f})")
            return result
            
        except Exception as e:
            logger.error(f"难度评估失败: {str(e)}")
            return self._get_default_result()
    
    def _extract_features(self, question_text: str, answer_text: str = None) -> DifficultyFeatures:
        """提取难度特征"""
        features = DifficultyFeatures()
        
        # 分析题目文本
        if question_text:
            self._analyze_text_complexity(question_text, features)
            self._analyze_chemistry_vocabulary(question_text, features)
            self._analyze_concepts(question_text, features)
            self._analyze_calculation_complexity(question_text, features)
            self._analyze_structural_complexity(question_text, features)
            self._analyze_reasoning_complexity(question_text, features)
            self._analyze_chapter_tags(question_text, features)
        
        # 分析答案文本
        if answer_text:
            self._analyze_answer_complexity(answer_text, features)
        
        return features
    
    def _analyze_text_complexity(self, text: str, features: DifficultyFeatures):
        """分析文本复杂度"""
        # 基础文本统计
        features.text_length = len(text)
        
        # 句子分割（考虑中文标点）
        sentences = re.split(r'[。！？；\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        features.sentence_count = len(sentences)
        
        if features.sentence_count > 0:
            features.avg_sentence_length = features.text_length / features.sentence_count
    
    def _analyze_chemistry_vocabulary(self, text: str, features: DifficultyFeatures):
        """分析化学词汇复杂度"""
        vocab_analysis = self.vocab_db.analyze_text_complexity(text)
        
        features.chemistry_vocab_ratio = vocab_analysis['chemistry_ratio']
        features.avg_chemistry_complexity = vocab_analysis['average_complexity']
        features.max_chemistry_complexity = vocab_analysis['max_complexity']
        features.technical_terms_count = vocab_analysis['chemistry_words']
    
    def _analyze_concepts(self, text: str, features: DifficultyFeatures):
        """分析概念深度"""
        concept_analysis = self.concepts_db.analyze_concept_depth(text)
        
        features.concept_count = concept_analysis['total_concepts']
        features.avg_concept_level = concept_analysis['average_level']
        features.max_concept_level = concept_analysis['max_level']
        features.missing_prerequisites = len(concept_analysis['prerequisites_missing'])
    
    def _analyze_calculation_complexity(self, text: str, features: DifficultyFeatures):
        """分析计算复杂度"""
        # 计算步骤识别
        calculation_indicators = 0
        for keyword in self.calculation_keywords:
            calculation_indicators += len(re.findall(keyword, text))
        
        # 基于计算关键词数量估算计算步骤
        if calculation_indicators > 0:
            features.calculation_steps = min(calculation_indicators, 10)
        
        # 公式识别
        formula_patterns = [
            r'[A-Z][a-z]*\s*=\s*[^=\n]+',  # 化学方程式
            r'[a-zA-Z]\s*=\s*[^=\n]+',       # 数学公式
            r'\d+\.?\d*\s*[+\-*/]\s*\d+\.?\d*',  # 数值计算
        ]
        
        for pattern in formula_patterns:
            matches = re.findall(pattern, text)
            features.formula_count += len(matches)
        
        # 数值和单位识别
        features.numerical_values = len(re.findall(r'\d+\.?\d*', text))
        features.units_count = len(re.findall(r'[mgLmolpHkMcm%/°C]+', text, re.IGNORECASE))
    
    def _analyze_structural_complexity(self, text: str, features: DifficultyFeatures):
        """分析结构复杂度"""
        # 题目部分识别
        part_patterns = [
            r'第[一二三四五六七八九十]+[部分题]',
            r'\([一二三四五六七八九十]+\)',
            r'\d+\.',  # 数字编号
            r'[A-D]\.',  # 选项
        ]
        
        for pattern in part_patterns:
            matches = re.findall(pattern, text)
            features.question_parts = max(features.question_parts, len(matches))
        
        # 子问题识别
        subq_patterns = [
            r'[\n\s]+[（(]\d+[)）]',
            r'[\n\s]+\d+[、.]',
            r'[\n\s]+[一二三四五六七八九十]+[、.]',
        ]
        
        for pattern in subq_patterns:
            matches = re.findall(pattern, text)
            features.sub_questions = max(features.sub_questions, len(matches) + 1)
        
        # 图表识别（基于关键词）
        features.has_diagram = bool(re.search(r'[图图][表表][示展]|示意图|结构图', text))
        features.has_table = bool(re.search(r'[表表][格格]|数据表', text))
    
    def _analyze_reasoning_complexity(self, text: str, features: DifficultyFeatures):
        """分析推理复杂度"""
        # 推理步骤识别
        reasoning_indicators = 0
        for keyword in self.reasoning_keywords:
            reasoning_indicators += len(re.findall(keyword, text))
        
        features.reasoning_steps = min(reasoning_indicators, 8)
        
        # 条件逻辑识别
        features.conditional_logic = bool(re.search('|'.join(self.conditional_keywords), text))
        
        # 多步骤推理识别
        multi_step_patterns = [
            r'首先.*然后.*最后',
            r'第一步.*第二步.*第三步',
            r'先.*再.*最后',
            r'经过.*得到.*因此'
        ]
        
        for pattern in multi_step_patterns:
            if re.search(pattern, text):
                features.multi_step_reasoning = True
                break
        
        # 抽象思维识别
        abstract_keywords = [
            '抽象', '理论', '模型', '假设', '推论', '推广', '一般化',
            '普遍性', '特殊性', '本质', '规律'
        ]
        
        for keyword in abstract_keywords:
            if keyword in text:
                features.abstract_thinking = True
                break
    
    def _analyze_answer_complexity(self, answer_text: str, features: DifficultyFeatures):
        """分析答案复杂度"""
        # 答案长度和详细程度
        answer_length = len(answer_text)
        
        # 如果答案很长，可能表示题目需要详细解释
        if answer_length > 200:
            features.reasoning_steps = max(features.reasoning_steps, 3)
        
        # 答案中的计算步骤
        step_keywords = ['解:', '解', '步骤', '第一步', '第二步', '第三步', '因此', '所以', '得']
        step_count = sum(len(re.findall(keyword, answer_text)) for keyword in step_keywords)
        
        if step_count > 0:
            features.calculation_steps = max(features.calculation_steps, step_count)

    def _analyze_chapter_tags(self, text: str, features: DifficultyFeatures):
        """分析题目涉及的高中化学章节标签"""
        tags: List[str] = []
        counts: Dict[str, int] = {}
        for chapter, kws in self.chapter_keywords.items():
            count = 0
            for kw in kws:
                count += len(re.findall(re.escape(kw), text))
            if count > 0:
                tags.append(chapter)
                counts[chapter] = count
        primary = ''
        if counts:
            primary = max(counts.items(), key=lambda x: x[1])[0]
        features.chapter_tags = tags
        features.primary_chapter = primary
    
    def _calculate_dimension_scores(self, features: DifficultyFeatures) -> Dict[str, float]:
        """计算各维度分数"""
        scores = {}
        
        # 文本复杂度分数 (0-100)
        text_score = self._calculate_text_score(features)
        scores['text_complexity'] = text_score
        
        # 词汇复杂度分数 (0-100)
        vocab_score = self._calculate_vocab_score(features)
        scores['vocabulary_complexity'] = vocab_score
        
        # 概念深度分数 (0-100)
        concept_score = self._calculate_concept_score(features)
        scores['concept_depth'] = concept_score
        
        # 计算复杂度分数 (0-100)
        calc_score = self._calculate_calculation_score(features)
        scores['calculation_complexity'] = calc_score
        
        # 结构复杂度分数 (0-100)
        struct_score = self._calculate_structural_score(features)
        scores['structural_complexity'] = struct_score
        
        # 推理复杂度分数 (0-100)
        reason_score = self._calculate_reasoning_score(features)
        scores['reasoning_complexity'] = reason_score
        
        return scores
    
    def _calculate_text_score(self, features: DifficultyFeatures) -> float:
        """计算文本复杂度分数"""
        score = 0.0
        
        # 文本长度分数 (0-40分)
        if features.text_length <= 100:
            score += features.text_length * 0.3
        elif features.text_length <= 300:
            score += 30 + (features.text_length - 100) * 0.05
        else:
            score += 40
        
        # 句子复杂度分数 (0-30分)
        if features.avg_sentence_length <= 20:
            score += features.avg_sentence_length * 1.0
        elif features.avg_sentence_length <= 40:
            score += 20 + (features.avg_sentence_length - 20) * 0.5
        else:
            score += 30
        
        # 句子数量分数 (0-30分)
        if features.sentence_count <= 3:
            score += features.sentence_count * 8
        elif features.sentence_count <= 6:
            score += 24 + (features.sentence_count - 3) * 2
        else:
            score += 30
        
        return min(score, 100)
    
    def _calculate_vocab_score(self, features: DifficultyFeatures) -> float:
        """计算词汇复杂度分数"""
        score = 0.0
        
        # 化学词汇比例分数 (0-40分)
        score += features.chemistry_vocab_ratio * 100 * 0.4
        
        # 平均复杂度分数 (0-30分)
        score += features.avg_chemistry_complexity * 6
        
        # 最大复杂度分数 (0-20分)
        score += features.max_chemistry_complexity * 4
        
        # 专业术语数量分数 (0-10分)
        score += min(features.technical_terms_count * 0.5, 10)
        
        return min(score, 100)
    
    def _calculate_concept_score(self, features: DifficultyFeatures) -> float:
        """计算概念深度分数"""
        score = 0.0
        
        # 概念数量分数 (0-30分)
        score += min(features.concept_count * 6, 30)
        
        # 平均概念级别分数 (0-25分)
        score += features.avg_concept_level * 5
        
        # 最大概念级别分数 (0-25分)
        score += features.max_concept_level * 5
        
        # 先修知识缺失扣分 (最多扣20分)
        score -= features.missing_prerequisites * 4
        
        return max(0, min(score, 100))
    
    def _calculate_calculation_score(self, features: DifficultyFeatures) -> float:
        """计算计算复杂度分数"""
        score = 0.0
        
        # 计算步骤分数 (0-40分)
        if features.calculation_steps <= 2:
            score += features.calculation_steps * 15
        elif features.calculation_steps <= 5:
            score += 30 + (features.calculation_steps - 2) * 3
        else:
            score += 40
        
        # 公式数量分数 (0-30分)
        score += min(features.formula_count * 6, 30)
        
        # 数值计算分数 (0-20分)
        score += min(features.numerical_values * 2, 20)
        
        # 单位复杂度分数 (0-10分)
        score += min(features.units_count * 1, 10)
        
        return min(score, 100)
    
    def _calculate_structural_score(self, features: DifficultyFeatures) -> float:
        """计算结构复杂度分数"""
        score = 0.0
        
        # 题目部分分数 (0-40分)
        if features.question_parts <= 2:
            score += features.question_parts * 15
        elif features.question_parts <= 4:
            score += 30 + (features.question_parts - 2) * 5
        else:
            score += 40
        
        # 子问题分数 (0-30分)
        if features.sub_questions <= 2:
            score += features.sub_questions * 10
        elif features.sub_questions <= 5:
            score += 20 + (features.sub_questions - 2) * 3
        else:
            score += 30
        
        # 图表复杂度分数 (0-30分)
        if features.has_diagram:
            score += 15
        if features.has_table:
            score += 15
        
        return min(score, 100)
    
    def _calculate_reasoning_score(self, features: DifficultyFeatures) -> float:
        """计算推理复杂度分数"""
        score = 0.0
        
        # 推理步骤分数 (0-40分)
        score += min(features.reasoning_steps * 5, 40)
        
        # 条件逻辑分数 (0-20分)
        if features.conditional_logic:
            score += 20
        
        # 多步骤推理分数 (0-20分)
        if features.multi_step_reasoning:
            score += 20
        
        # 抽象思维分数 (0-20分)
        if features.abstract_thinking:
            score += 20
        
        return min(score, 100)
    
    def _calculate_total_score(self, dimension_scores: Dict[str, float]) -> float:
        """计算综合难度分数"""
        total_score = 0.0
        
        for dimension, weight in self.weights.items():
            if dimension in dimension_scores:
                total_score += dimension_scores[dimension] * weight
        
        return min(total_score, 100)
    
    def _determine_difficulty_level(self, total_score: float) -> str:
        """确定难度级别"""
        for level, thresholds in self.difficulty_thresholds.items():
            if thresholds['min'] <= total_score < thresholds['max']:
                return level
        
        # 边界情况
        if total_score >= 100:
            return 'advanced'
        return 'beginner'
    
    def _generate_detailed_analysis(self, features: DifficultyFeatures, 
                                  scores: Dict[str, float], total_score: float) -> Dict[str, str]:
        """生成详细分析"""
        analysis = {}
        
        # 主要难度因素
        max_dimension = max(scores.items(), key=lambda x: x[1])
        analysis['primary_difficulty_factor'] = f"主要难度因素: {self._get_dimension_name(max_dimension[0])} ({max_dimension[1]:.1f}分)"
        
        # 文本复杂度分析
        if features.text_length > 200:
            analysis['text_analysis'] = "题目文本较长，需要较强的阅读理解能力"
        elif features.text_length < 50:
            analysis['text_analysis'] = "题目文本简洁，信息密度可能较高"
        else:
            analysis['text_analysis'] = "题目文本长度适中"
        
        # 词汇复杂度分析
        if features.chemistry_vocab_ratio > 0.3:
            analysis['vocab_analysis'] = "包含大量专业化学词汇，需要扎实的化学基础"
        elif features.chemistry_vocab_ratio > 0.1:
            analysis['vocab_analysis'] = "包含一定量的化学专业术语"
        else:
            analysis['vocab_analysis'] = "主要使用基础化学术语"
        
        # 概念深度分析
        if features.max_concept_level >= 4:
            analysis['concept_analysis'] = "涉及高级化学概念和理论"
        elif features.max_concept_level >= 3:
            analysis['concept_analysis'] = "涉及中级化学概念"
        else:
            analysis['concept_analysis'] = "主要涉及基础化学概念"
        
        # 计算复杂度分析
        if features.calculation_steps > 5:
            analysis['calc_analysis'] = "需要多步骤计算和复杂的数学处理"
        elif features.calculation_steps > 2:
            analysis['calc_analysis'] = "需要一定的计算步骤"
        else:
            analysis['calc_analysis'] = "计算要求相对简单"
        
        return analysis
    
    def _get_dimension_name(self, dimension_key: str) -> str:
        """获取维度中文名称"""
        names = {
            'text_complexity': '文本复杂度',
            'vocabulary_complexity': '词汇复杂度',
            'concept_depth': '概念深度',
            'calculation_complexity': '计算复杂度',
            'structural_complexity': '结构复杂度',
            'reasoning_complexity': '推理复杂度'
        }
        return names.get(dimension_key, dimension_key)
    
    def _generate_recommendations(self, features: DifficultyFeatures, total_score: float) -> List[str]:
        """生成学习建议"""
        recommendations = []
        
        if total_score < 35:
            recommendations.append("适合初学者练习基础概念和简单计算")
            recommendations.append("建议先掌握相关的基础化学知识")
        elif total_score < 65:
            recommendations.append("适合有一定基础的学生进行综合练习")
            recommendations.append("建议复习相关的化学概念和计算方法")
        else:
            recommendations.append("适合高级学习者挑战复杂问题")
            recommendations.append("建议系统复习相关理论知识，加强综合应用能力")
        
        # 针对性建议
        if features.missing_prerequisites > 0:
            recommendations.append("需要先修知识的学习和巩固")
        
        if features.calculation_steps > 5:
            recommendations.append("建议加强复杂计算和多步骤问题的训练")
        
        if features.max_concept_level >= 4:
            recommendations.append("涉及高级理论概念，建议深入理解相关理论")
        
        return recommendations
    
    def _features_to_dict(self, features: DifficultyFeatures) -> Dict[str, any]:
        """将特征转换为字典"""
        return {
            'text_length': features.text_length,
            'sentence_count': features.sentence_count,
            'avg_sentence_length': features.avg_sentence_length,
            'chemistry_vocab_ratio': features.chemistry_vocab_ratio,
            'avg_chemistry_complexity': features.avg_chemistry_complexity,
            'max_chemistry_complexity': features.max_chemistry_complexity,
            'technical_terms_count': features.technical_terms_count,
            'concept_count': features.concept_count,
            'avg_concept_level': features.avg_concept_level,
            'max_concept_level': features.max_concept_level,
            'missing_prerequisites': features.missing_prerequisites,
            'calculation_steps': features.calculation_steps,
            'formula_count': features.formula_count,
            'numerical_values': features.numerical_values,
            'units_count': features.units_count,
            'question_parts': features.question_parts,
            'sub_questions': features.sub_questions,
            'has_diagram': features.has_diagram,
            'has_table': features.has_table,
            'reasoning_steps': features.reasoning_steps,
            'conditional_logic': features.conditional_logic,
            'multi_step_reasoning': features.multi_step_reasoning,
            'abstract_thinking': features.abstract_thinking,
            'chapter_tags': features.chapter_tags or [],
            'primary_chapter': features.primary_chapter
        }
    
    def _get_default_result(self) -> Dict[str, any]:
        """获取默认结果（当评估失败时）"""
        return {
            'total_score': 30.0,
            'difficulty_level': 'beginner',
            'dimension_scores': {
                'text_complexity': 30.0,
                'vocabulary_complexity': 30.0,
                'concept_depth': 30.0,
                'calculation_complexity': 30.0,
                'structural_complexity': 30.0,
                'reasoning_complexity': 30.0
            },
            'features': {},
            'detailed_analysis': {'error': '评估失败，使用默认结果'},
            'recommendations': ['无法进行准确评估，建议人工判断']
        }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """更新权重配置"""
        for dimension, weight in new_weights.items():
            if dimension in self.weights:
                self.weights[dimension] = weight
        
        logger.info("难度评估权重已更新")
    
    def get_weight_configuration(self) -> Dict[str, float]:
        """获取当前权重配置"""
        return self.weights.copy()
    
    def get_difficulty_thresholds(self) -> Dict[str, Dict[str, int]]:
        """获取难度级别阈值"""
        return self.difficulty_thresholds.copy()
    
    def update_difficulty_thresholds(self, new_thresholds: Dict[str, Dict[str, int]]):
        """更新难度级别阈值"""
        for level, thresholds in new_thresholds.items():
            if level in self.difficulty_thresholds:
                self.difficulty_thresholds[level] = thresholds
        
        logger.info("难度级别阈值已更新")