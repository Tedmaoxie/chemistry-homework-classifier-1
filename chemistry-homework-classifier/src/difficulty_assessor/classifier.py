"""
三级分类系统
实现基础、中级、高级题目的自动分类
"""

import logging
import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .assessor import MultiDimensionalDifficultyAssessor, DifficultyFeatures

logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """难度级别枚举"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class ClassificationRule:
    """分类规则数据类"""
    name: str
    condition: callable
    priority: int
    description: str
    examples: List[str]


@dataclass
class ClassificationResult:
    """分类结果数据类"""
    level: DifficultyLevel
    confidence: float
    reasons: List[str]
    matching_rules: List[str]
    recommendations: List[str]
    detailed_analysis: Dict[str, any]


class ThreeTierClassifier:
    """三级分类器"""
    
    def __init__(self, assessor: MultiDimensionalDifficultyAssessor = None):
        """
        初始化分类器
        
        Args:
            assessor: 难度评估器
        """
        self.assessor = assessor or MultiDimensionalDifficultyAssessor()
        
        # 初始化分类规则
        self.classification_rules = self._initialize_classification_rules()
        
        # 分类置信度阈值
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        # 特殊题目类型识别
        self.special_question_types = {
            'basic_concept': self._is_basic_concept_question,
            'simple_calculation': self._is_simple_calculation_question,
            'comprehensive_application': self._is_comprehensive_application_question,
            'complex_analysis': self._is_complex_analysis_question,
            'experimental_design': self._is_experimental_design_question,
            'theoretical_derivation': self._is_theoretical_derivation_question
        }

        # 超出高中范围的高等化学关键词（用于范围限定）
        self.out_of_scope_keywords = [
            '分子轨道', '量子化学', '密度泛函', 'DFT', '晶体场', '配位场', '群论', '能带',
            '核磁共振', 'NMR', '质谱', 'MS', 'X射线光电子谱', 'XPS', 'X射线衍射', 'XRD',
            '拉曼', '红外谱图解析', '电子自旋共振', 'ESR', '薛定谔', '波函数', '量子态'
        ]
        
        logger.info("三级分类器初始化完成")
    
    def classify_question(self, question_text: str, answer_text: str = None) -> ClassificationResult:
        """
        分类题目
        
        Args:
            question_text: 题目文本
            answer_text: 答案文本（可选）
            
        Returns:
            分类结果
        """
        try:
            # 进行难度评估
            difficulty_assessment = self.assessor.assess_difficulty(question_text, answer_text)
            
            # 识别特殊题目类型
            special_types = self._identify_special_question_types(question_text, answer_text)
            
            # 应用分类规则
            rule_matches = self._apply_classification_rules(
                difficulty_assessment, special_types, question_text, answer_text
            )
            
            # 确定最终分类
            final_classification = self._determine_final_classification(
                difficulty_assessment, rule_matches, special_types
            )
            
            # 生成分类理由
            reasons = self._generate_classification_reasons(
                difficulty_assessment, rule_matches, special_types
            )
            
            # 生成建议
            recommendations = self._generate_classification_recommendations(final_classification)
            
            result = ClassificationResult(
                level=final_classification['level'],
                confidence=final_classification['confidence'],
                reasons=reasons,
                matching_rules=rule_matches,
                recommendations=recommendations,
                detailed_analysis=difficulty_assessment
            )
            
            logger.info(f"题目分类完成: {result.level.value} (置信度: {result.confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"题目分类失败: {str(e)}")
            return self._get_default_classification()
    
    def _initialize_classification_rules(self) -> List[ClassificationRule]:
        """初始化分类规则"""
        rules = []

        # 范围限定：超出高中化学范围的题目统一识别为高级
        rules.append(
            ClassificationRule(
                name="高中范围外识别",
                condition=lambda assessment, types, q, a: self._is_out_of_scope_question(assessment, q),
                priority=100,
                description="识别超出高中化学知识范围的题目（涉及大学/高等化学概念或方法）",
                examples=["应用分子轨道理论定量分析", "使用DFT计算反应势能面", "解析NMR/质谱图确定结构"]
            )
        )
        
        # 初级题目规则
        rules.extend([
            ClassificationRule(
                name="基础概念识别",
                condition=lambda assessment, types, q, a: self._is_basic_concept_rule(assessment, types),
                priority=10,
                description="识别基础概念题目",
                examples=["什么是化学键？", "简述原子结构的基本组成"]
            ),
            ClassificationRule(
                name="简单计算识别",
                condition=lambda assessment, types, q, a: self._is_simple_calculation_rule(assessment, types),
                priority=9,
                description="识别简单计算题目",
                examples=["计算NaCl的摩尔质量", "求pH=7的溶液中H+浓度"]
            ),
            ClassificationRule(
                name="定义记忆识别",
                condition=lambda assessment, types, q, a: self._is_definition_memory_rule(assessment, types, q),
                priority=8,
                description="识别定义记忆类题目",
                examples=["定义化学平衡常数", "什么是氧化还原反应"]
            ),
            ClassificationRule(
                name="单一步骤识别",
                condition=lambda assessment, types, q, a: self._is_single_step_rule(assessment),
                priority=7,
                description="识别单一步骤解答题目",
                examples=["写出水的电离方程式", "判断下列物质的酸碱性"]
            )
        ])
        
        # 中级题目规则
        rules.extend([
            ClassificationRule(
                name="综合应用识别",
                condition=lambda assessment, types, q, a: self._is_comprehensive_application_rule(assessment, types),
                priority=6,
                description="识别综合应用题目",
                examples=["根据给定条件计算反应速率", "分析化学平衡的移动方向"]
            ),
            ClassificationRule(
                name="多步骤计算识别",
                condition=lambda assessment, types, q, a: self._is_multi_step_calculation_rule(assessment),
                priority=5,
                description="识别多步骤计算题目",
                examples=["计算缓冲溶液的pH值", "求化学反应的平衡常数"]
            ),
            ClassificationRule(
                name="比较分析识别",
                condition=lambda assessment, types, q, a: self._is_comparison_analysis_rule(assessment, types, q),
                priority=4,
                description="识别比较分析题目",
                examples=["比较不同物质的酸性强弱", "分析影响反应速率的因素"]
            ),
            ClassificationRule(
                name="中等概念识别",
                condition=lambda assessment, types, q, a: self._is_intermediate_concept_rule(assessment),
                priority=3,
                description="识别中级概念题目",
                examples=["解释化学平衡的微观本质", "分析分子间作用力的类型"]
            )
        ])
        
        # 高级题目规则
        rules.extend([
            ClassificationRule(
                name="复杂分析识别",
                condition=lambda assessment, types, q, a: self._is_complex_analysis_rule(assessment, types),
                priority=2,
                description="识别复杂分析题目",
                examples=["设计实验验证化学理论", "综合分析多因素影响"]
            ),
            ClassificationRule(
                name="理论推导识别",
                condition=lambda assessment, types, q, a: self._is_theoretical_derivation_rule(assessment, types, q),
                priority=1,
                description="识别理论推导题目",
                examples=["推导化学动力学方程", "证明热力学关系式"]
            ),
            ClassificationRule(
                name="实验设计识别",
                condition=lambda assessment, types, q, a: self._is_experimental_design_rule(assessment, types, q),
                priority=1,
                description="识别实验设计题目",
                examples=["设计实验测定反应活化能", "制定物质分离纯化方案"]
            ),
            ClassificationRule(
                name="高级概念识别",
                condition=lambda assessment, types, q, a: self._is_advanced_concept_rule(assessment),
                priority=0,
                description="识别高级概念题目",
                examples=["应用分子轨道理论解释性质", "用量子化学方法分析结构"]
            )
        ])
        
        # 按优先级排序
        rules.sort(key=lambda x: x.priority, reverse=True)
        
        return rules
    
    def _identify_special_question_types(self, question_text: str, answer_text: str = None) -> Set[str]:
        """识别特殊题目类型"""
        special_types = set()
        
        for type_name, type_checker in self.special_question_types.items():
            if type_checker(question_text, answer_text):
                special_types.add(type_name)
        
        return special_types
    
    def _is_basic_concept_question(self, question_text: str, answer_text: str = None) -> bool:
        """识别基础概念题目"""
        basic_keywords = [
            '什么是', '定义', '简述', '说明', '解释', '描述',
            '基本概念', '基本性质', '基本组成'
        ]
        
        concept_keywords = [
            '原子', '分子', '离子', '化学键', '元素', '化合物',
            '酸', '碱', '盐', '氧化物', '化学反应',
            '元素周期律', '有机化学', '官能团', '反应原理'
        ]
        
        has_basic_keyword = any(keyword in question_text for keyword in basic_keywords)
        has_concept_keyword = any(keyword in question_text for keyword in concept_keywords)
        
        return has_basic_keyword and has_concept_keyword
    
    def _is_simple_calculation_question(self, question_text: str, answer_text: str = None) -> bool:
        """识别简单计算题目"""
        calc_keywords = ['计算', '求', '解', '得出', '结果是']
        simple_indicators = ['摩尔质量', '浓度', 'pH', '质量', '体积']
        
        has_calc_keyword = any(keyword in question_text for keyword in calc_keywords)
        has_simple_indicator = any(keyword in question_text for keyword in simple_indicators)
        
        # 检查是否涉及复杂概念
        complex_concepts = ['平衡常数', '反应速率', '活化能', '电极电势']
        has_complex_concept = any(concept in question_text for concept in complex_concepts)
        
        return has_calc_keyword and has_simple_indicator and not has_complex_concept
    
    def _is_comprehensive_application_question(self, question_text: str, answer_text: str = None) -> bool:
        """识别综合应用题目"""
        comprehensive_keywords = [
            '综合分析', '综合考虑', '应用', '利用', '根据',
            '结合', '联系', '关联', '影响'
        ]
        
        has_comprehensive_keyword = any(keyword in question_text for keyword in comprehensive_keywords)
        
        # 检查是否涉及多个概念
        concept_count = len(re.findall(r'(化学平衡|反应速率|酸碱理论|氧化还原|元素周期律|有机化学|官能团|同分异构)', question_text))
        
        return has_comprehensive_keyword or concept_count >= 2
    
    def _is_complex_analysis_question(self, question_text: str, answer_text: str = None) -> bool:
        """识别复杂分析题目"""
        complex_keywords = [
            '设计', '制定', '方案', '方法', '策略',
            '优化', '改进', '比较', '选择', '判断'
        ]
        
        analysis_keywords = [
            '分析', '研究', '探讨', '讨论', '论证',
            '证明', '推导', '解释', '说明'
        ]
        
        has_complex_keyword = any(keyword in question_text for keyword in complex_keywords)
        has_analysis_keyword = any(keyword in question_text for keyword in analysis_keywords)
        
        return has_complex_keyword and has_analysis_keyword
    
    def _is_experimental_design_question(self, question_text: str, answer_text: str = None) -> bool:
        """识别实验设计题目"""
        experiment_keywords = [
            '实验', '测定', '测量', '验证', '检验',
            '设计', '方案', '步骤', '操作', '现象'
        ]
        
        design_keywords = ['设计', '制定', '方案', '方法']
        
        has_experiment_keyword = any(keyword in question_text for keyword in experiment_keywords)
        has_design_keyword = any(keyword in question_text for keyword in design_keywords)
        
        return has_experiment_keyword and has_design_keyword
    
    def _is_theoretical_derivation_question(self, question_text: str, answer_text: str = None) -> bool:
        """识别理论推导题目"""
        theory_keywords = [
            '理论', '原理', '定律', '定理', '公式',
            '方程', '关系', '规律', '模型'
        ]
        
        derivation_keywords = [
            '推导', '证明', '论证', '得出', '建立',
            '解释', '说明', '阐述'
        ]
        
        has_theory_keyword = any(keyword in question_text for keyword in theory_keywords)
        has_derivation_keyword = any(keyword in question_text for keyword in derivation_keywords)
        
        return has_theory_keyword and has_derivation_keyword
    
    def _apply_classification_rules(self, assessment: Dict[str, any], special_types: Set[str],
                                  question_text: str, answer_text: str = None) -> List[str]:
        """应用分类规则"""
        matching_rules = []
        
        for rule in self.classification_rules:
            try:
                if rule.condition(assessment, special_types, question_text, answer_text):
                    matching_rules.append(rule.name)
            except Exception as e:
                logger.warning(f"规则 {rule.name} 应用失败: {str(e)}")
        
        return matching_rules

    def _is_out_of_scope_question(self, assessment: Dict[str, any], question_text: str) -> bool:
        """判断题目是否超出高中化学知识范围"""
        features = assessment.get('features', {})
        max_concept_level = features.get('max_concept_level', 0)
        max_vocab_complexity = features.get('max_chemistry_complexity', 0)
        keyword_hit = any(k in question_text for k in self.out_of_scope_keywords)

        # 超出范围条件：概念层级或词汇复杂度达到高等水平，或出现高等化学关键词
        return (max_concept_level >= 4) or (max_vocab_complexity >= 4) or keyword_hit
    
    def _is_basic_concept_rule(self, assessment: Dict[str, any], special_types: Set[str]) -> bool:
        """基础概念规则"""
        total_score = assessment.get('total_score', 0)
        concept_score = assessment.get('dimension_scores', {}).get('concept_depth', 0)
        
        return (total_score < 40 and 
                concept_score < 50 and 
                'basic_concept' in special_types)
    
    def _is_simple_calculation_rule(self, assessment: Dict[str, any], special_types: Set[str]) -> bool:
        """简单计算规则"""
        total_score = assessment.get('total_score', 0)
        calc_score = assessment.get('dimension_scores', {}).get('calculation_complexity', 0)
        
        return (total_score < 45 and 
                calc_score < 60 and 
                'simple_calculation' in special_types)
    
    def _is_definition_memory_rule(self, assessment: Dict[str, any], special_types: Set[str], 
                                 question_text: str) -> bool:
        """定义记忆规则"""
        definition_keywords = ['定义', '什么是', '简述', '说明']
        has_definition_keyword = any(keyword in question_text for keyword in definition_keywords)
        
        total_score = assessment.get('total_score', 0)
        reasoning_score = assessment.get('dimension_scores', {}).get('reasoning_complexity', 0)
        
        return (has_definition_keyword and 
                total_score < 35 and 
                reasoning_score < 30)
    
    def _is_single_step_rule(self, assessment: Dict[str, any]) -> bool:
        """单一步骤规则"""
        features = assessment.get('features', {})
        calc_steps = features.get('calculation_steps', 0)
        reasoning_steps = features.get('reasoning_steps', 0)
        total_score = assessment.get('total_score', 0)
        
        return (calc_steps <= 2 and 
                reasoning_steps <= 1 and 
                total_score < 40)
    
    def _is_comprehensive_application_rule(self, assessment: Dict[str, any], special_types: Set[str]) -> bool:
        """综合应用规则"""
        total_score = assessment.get('total_score', 0)
        concept_score = assessment.get('dimension_scores', {}).get('concept_depth', 0)
        
        return (40 <= total_score < 70 and 
                concept_score >= 50 and 
                'comprehensive_application' in special_types)
    
    def _is_multi_step_calculation_rule(self, assessment: Dict[str, any]) -> bool:
        """多步骤计算规则"""
        features = assessment.get('features', {})
        calc_steps = features.get('calculation_steps', 0)
        total_score = assessment.get('total_score', 0)
        calc_score = assessment.get('dimension_scores', {}).get('calculation_complexity', 0)
        
        return (calc_steps >= 3 and 
                calc_steps <= 5 and 
                35 <= total_score < 70 and 
                calc_score >= 50)
    
    def _is_comparison_analysis_rule(self, assessment: Dict[str, any], special_types: Set[str], 
                                   question_text: str) -> bool:
        """比较分析规则"""
        comparison_keywords = ['比较', '对比', '分析', '区别', '异同']
        has_comparison_keyword = any(keyword in question_text for keyword in comparison_keywords)
        
        total_score = assessment.get('total_score', 0)
        reasoning_score = assessment.get('dimension_scores', {}).get('reasoning_complexity', 0)
        
        return (has_comparison_keyword and 
                40 <= total_score < 70 and 
                reasoning_score >= 40)
    
    def _is_intermediate_concept_rule(self, assessment: Dict[str, any]) -> bool:
        """中级概念规则"""
        total_score = assessment.get('total_score', 0)
        concept_score = assessment.get('dimension_scores', {}).get('concept_depth', 0)
        max_concept_level = assessment.get('features', {}).get('max_concept_level', 0)
        
        return (40 <= total_score < 65 and 
                concept_score >= 45 and 
                max_concept_level in [2, 3])
    
    def _is_complex_analysis_rule(self, assessment: Dict[str, any], special_types: Set[str]) -> bool:
        """复杂分析规则"""
        total_score = assessment.get('total_score', 0)
        reasoning_score = assessment.get('dimension_scores', {}).get('reasoning_complexity', 0)
        
        return (total_score >= 65 and 
                reasoning_score >= 60 and 
                'complex_analysis' in special_types)
    
    def _is_theoretical_derivation_rule(self, assessment: Dict[str, any], special_types: Set[str], 
                                      question_text: str) -> bool:
        """理论推导规则"""
        derivation_keywords = ['推导', '证明', '论证', '建立']
        has_derivation_keyword = any(keyword in question_text for keyword in derivation_keywords)
        
        total_score = assessment.get('total_score', 0)
        concept_score = assessment.get('dimension_scores', {}).get('concept_depth', 0)
        
        return (has_derivation_keyword and 
                total_score >= 60 and 
                concept_score >= 65)
    
    def _is_experimental_design_rule(self, assessment: Dict[str, any], special_types: Set[str], 
                                   question_text: str) -> bool:
        """实验设计规则"""
        total_score = assessment.get('total_score', 0)
        reasoning_score = assessment.get('dimension_scores', {}).get('reasoning_complexity', 0)
        
        return (total_score >= 65 and 
                reasoning_score >= 55 and 
                'experimental_design' in special_types)
    
    def _is_advanced_concept_rule(self, assessment: Dict[str, any]) -> bool:
        """高级概念规则"""
        total_score = assessment.get('total_score', 0)
        concept_score = assessment.get('dimension_scores', {}).get('concept_depth', 0)
        max_concept_level = assessment.get('features', {}).get('max_concept_level', 0)
        
        return (total_score >= 65 and 
                concept_score >= 70 and 
                max_concept_level >= 4)
    
    def _determine_final_classification(self, assessment: Dict[str, any], rule_matches: List[str], 
                                       special_types: Set[str]) -> Dict[str, any]:
        """确定最终分类（依据评估器阈值与规则调整）"""
        # 基于评估器计算出的难度级别进行初步分类
        level_str = assessment.get('difficulty_level', DifficultyLevel.INTERMEDIATE.value)
        if level_str == DifficultyLevel.BEGINNER.value:
            base_level = DifficultyLevel.BEGINNER
            base_confidence = 0.8
        elif level_str == DifficultyLevel.INTERMEDIATE.value:
            base_level = DifficultyLevel.INTERMEDIATE
            base_confidence = 0.7
        else:
            base_level = DifficultyLevel.ADVANCED
            base_confidence = 0.8
        
        # 根据规则匹配调整分类
        confidence_adjustment = 0.0
        
        # 如果匹配到高级规则，提升分类级别
        advanced_rules = ['复杂分析识别', '理论推导识别', '实验设计识别', '高级概念识别', '高中范围外识别']
        if any(rule in rule_matches for rule in advanced_rules):
            if base_level != DifficultyLevel.ADVANCED:
                base_level = DifficultyLevel.ADVANCED
                confidence_adjustment += 0.2
        
        # 如果匹配到初级规则，降低分类级别
        beginner_rules = ['基础概念识别', '简单计算识别', '定义记忆识别', '单一步骤识别']
        if any(rule in rule_matches for rule in beginner_rules):
            if base_level != DifficultyLevel.BEGINNER:
                base_level = DifficultyLevel.BEGINNER
                confidence_adjustment += 0.2
        
        # 计算最终置信度
        final_confidence = min(base_confidence + confidence_adjustment, 1.0)
        
        return {
            'level': base_level,
            'confidence': final_confidence
        }
    
    def _generate_classification_reasons(self, assessment: Dict[str, any], rule_matches: List[str], 
                                         special_types: Set[str]) -> List[str]:
        """生成分类理由"""
        reasons = []
        
        # 基于评估结果的理由
        total_score = assessment.get('total_score', 0)
        reasons.append(f"综合难度评分: {total_score:.1f}分")
        # 主章节
        primary_chapter = assessment.get('features', {}).get('primary_chapter', '')
        if primary_chapter:
            reasons.append(f"主要章节: {primary_chapter}")
        
        # 主要难度因素
        dimension_scores = assessment.get('dimension_scores', {})
        if dimension_scores:
            max_dimension = max(dimension_scores.items(), key=lambda x: x[1])
            reasons.append(f"主要难度因素: {self._get_dimension_name(max_dimension[0])}")
        
        # 基于规则匹配的理由
        if rule_matches:
            reasons.append(f"匹配分类规则: {', '.join(rule_matches[:3])}")
        
        # 基于特殊类型的理由
        if special_types:
            type_descriptions = {
                'basic_concept': '基础概念题目',
                'simple_calculation': '简单计算题目',
                'comprehensive_application': '综合应用题目',
                'complex_analysis': '复杂分析题目',
                'experimental_design': '实验设计题目',
                'theoretical_derivation': '理论推导题目'
            }
            
            for type_name in special_types:
                if type_name in type_descriptions:
                    reasons.append(f"题目类型: {type_descriptions[type_name]}")
        
        return reasons
    
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
    
    def _generate_classification_recommendations(self, classification: Dict[str, any]) -> List[str]:
        """生成分类建议"""
        level = classification['level']
        confidence = classification['confidence']
        
        recommendations = []
        
        if level == DifficultyLevel.BEGINNER:
            recommendations.extend([
                "适合基础练习和概念巩固",
                "建议先掌握相关基础知识",
                "适合作为入门练习题"
            ])
        elif level == DifficultyLevel.INTERMEDIATE:
            recommendations.extend([
                "适合综合应用能力训练",
                "建议具备一定的基础知识",
                "适合作为进阶练习题"
            ])
        else:  # ADVANCED
            recommendations.extend([
                "适合高级思维训练",
                "建议系统掌握相关理论",
                "适合作为挑战性问题"
            ])
        
        # 根据置信度添加建议
        if confidence < 0.6:
            recommendations.append("分类置信度较低，建议人工复核")
        elif confidence > 0.9:
            recommendations.append("分类置信度很高，结果可靠")
        
        return recommendations
    
    def _get_default_classification(self) -> ClassificationResult:
        """获取默认分类结果"""
        return ClassificationResult(
            level=DifficultyLevel.INTERMEDIATE,
            confidence=0.3,
            reasons=["分类失败，使用默认结果"],
            matching_rules=[],
            recommendations=["建议人工判断题目难度"],
            detailed_analysis={}
        )
    
    def batch_classify(self, questions: List[Tuple[str, str]]) -> List[ClassificationResult]:
        """
        批量分类题目
        
        Args:
            questions: (题目文本, 答案文本) 列表
            
        Returns:
            分类结果列表
        """
        results = []
        
        for i, (question_text, answer_text) in enumerate(questions):
            try:
                result = self.classify_question(question_text, answer_text)
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"已分类 {i + 1}/{len(questions)} 道题目")
                    
            except Exception as e:
                logger.error(f"第 {i + 1} 题分类失败: {str(e)}")
                results.append(self._get_default_classification())
        
        logger.info(f"批量分类完成，共处理 {len(results)} 道题目")
        return results

    def enforce_difficulty_ratio(self, results: List[ClassificationResult], target_ratio: Dict[str, float] = None) -> List[ClassificationResult]:
        """
        根据目标难度比例对批量分类结果进行轻量再平衡调整。

        调整策略：
        - 仅在边界样本上调整（置信度最低的样本）。
        - 不调整匹配到高级规则（如实验设计/理论推导/高中范围外识别）的题目。
        - 保持原有理由与分析，仅更新级别。
        
        Args:
            results: 分类结果列表
            target_ratio: 目标比例，例如 {"beginner": 0.6, "intermediate": 0.3, "advanced": 0.1}
        Returns:
            调整后的分类结果列表（原列表的浅拷贝）。
        """
        if not results:
            return results

        ratio = target_ratio or {"beginner": 0.6, "intermediate": 0.3, "advanced": 0.1}
        total = len(results)
        target_counts = {
            'beginner': int(round(total * ratio['beginner'])),
            'intermediate': int(round(total * ratio['intermediate'])),
            'advanced': total - int(round(total * ratio['beginner'])) - int(round(total * ratio['intermediate']))
        }

        # 当前计数
        current = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        for r in results:
            current[r.level.value] += 1

        # 帮助函数：筛选可调整的样本（排除强高级规则命中）
        def adjustable(items: List[ClassificationResult]) -> List[ClassificationResult]:
            protected_rules = {'实验设计识别', '理论推导识别', '复杂分析识别', '高中范围外识别'}
            return [i for i in items if not any(rule in protected_rules for rule in i.matching_rules)]

        # 按置信度排序（低置信度优先调整）
        beginners = sorted([r for r in results if r.level == DifficultyLevel.BEGINNER], key=lambda x: x.confidence)
        intermediates = sorted([r for r in results if r.level == DifficultyLevel.INTERMEDIATE], key=lambda x: x.confidence)
        advanced = sorted([r for r in results if r.level == DifficultyLevel.ADVANCED], key=lambda x: x.confidence)

        beginners_adj = adjustable(beginners)
        intermediates_adj = adjustable(intermediates)
        advanced_adj = adjustable(advanced)

        # 需要增加或减少的数量
        def delta(kind: str) -> int:
            return target_counts[kind] - current[kind]

        # 先处理高级数量过多的情况：向中级/基础下调最低置信度的样本
        while delta('advanced') < 0 and advanced_adj:
            item = advanced_adj.pop(0)
            # 优先下调到中级，再到基础
            if current['intermediate'] < target_counts['intermediate']:
                item.level = DifficultyLevel.INTERMEDIATE
                current['advanced'] -= 1
                current['intermediate'] += 1
            else:
                item.level = DifficultyLevel.BEGINNER
                current['advanced'] -= 1
                current['beginner'] += 1

        # 若高级数量不足：从中级或基础中挑选少量上调（需要一定置信度）
        while delta('advanced') > 0:
            candidate = None
            # 优先从中级中挑选高置信度样本上调
            for i, item in enumerate(reversed(intermediates_adj)):
                if item.confidence >= 0.75:
                    candidate = intermediates_adj.pop(len(intermediates_adj) - 1 - i)
                    break
            # 其次从基础中挑选高置信度样本上调
            if candidate is None:
                for i, item in enumerate(reversed(beginners_adj)):
                    if item.confidence >= 0.85:
                        candidate = beginners_adj.pop(len(beginners_adj) - 1 - i)
                        break
            if candidate is None:
                break
            orig_level = candidate.level.value
            candidate.level = DifficultyLevel.ADVANCED
            current['advanced'] += 1
            current[orig_level] -= 1

        # 处理中级与基础的比例
        while delta('intermediate') < 0 and intermediates_adj:
            item = intermediates_adj.pop(0)
            item.level = DifficultyLevel.BEGINNER
            current['intermediate'] -= 1
            current['beginner'] += 1

        while delta('intermediate') > 0 and beginners_adj:
            # 基础中置信度较高的样本上调到中级
            item = beginners_adj.pop()
            if item.confidence >= 0.7:
                item.level = DifficultyLevel.INTERMEDIATE
                current['beginner'] -= 1
                current['intermediate'] += 1
            else:
                break

        return results
    
    def get_classification_statistics(self, results: List[ClassificationResult]) -> Dict[str, any]:
        """获取分类统计信息"""
        if not results:
            return {}
        
        stats = {
            'total_questions': len(results),
            'level_distribution': {
                'beginner': 0,
                'intermediate': 0,
                'advanced': 0
            },
            'average_confidence': 0.0,
            'confidence_distribution': {
                'high': 0,      # >= 0.8
                'medium': 0,    # 0.6-0.8
                'low': 0        # < 0.6
            }
        }
        
        total_confidence = 0.0
        
        for result in results:
            # 级别分布
            stats['level_distribution'][result.level.value] += 1
            
            # 置信度统计
            total_confidence += result.confidence
            
            if result.confidence >= 0.8:
                stats['confidence_distribution']['high'] += 1
            elif result.confidence >= 0.6:
                stats['confidence_distribution']['medium'] += 1
            else:
                stats['confidence_distribution']['low'] += 1
        
        stats['average_confidence'] = total_confidence / len(results)
        
        return stats

    def get_chapter_distribution(self, results: List[ClassificationResult]) -> Dict[str, any]:
        """统计各难度级别下的章节分布"""
        dist = {
            'beginner': defaultdict(int),
            'intermediate': defaultdict(int),
            'advanced': defaultdict(int),
            'overall': defaultdict(int)
        }
        for r in results:
            features = r.detailed_analysis.get('features', {}) if isinstance(r.detailed_analysis, dict) else {}
            chapter = features.get('primary_chapter', '') or '未识别'
            dist[r.level.value][chapter] += 1
            dist['overall'][chapter] += 1
        # 转换为普通字典
        for k in list(dist.keys()):
            dist[k] = dict(dist[k])
        return dist

    def enforce_chapter_balance(self, results: List[ClassificationResult], per_level_targets: Dict[str, Dict[str, float]] = None) -> List[ClassificationResult]:
        """
        根据每个难度级别的章节目标比例，轻量调整样本的难度级别，以提升章节均衡。

        约束：
        - 不调整命中强高级规则（实验设计/理论推导/复杂分析/高中范围外识别）。
        - 先执行整体难度比例的再平衡（60/30/10），再进行章节均衡。
        - 优先从相邻级别（beginner<->intermediate）迁移边界样本；对advanced仅在非受保护且置信度较高时参与迁移。
        """
        if not results:
            return results

        # 先确保整体难度比例
        self.enforce_difficulty_ratio(results, {"beginner": 0.6, "intermediate": 0.3, "advanced": 0.1})

        # 统计当前章节分布
        dist = self.get_chapter_distribution(results)

        # 构建目标比例（若未提供，则各级别下观察到的章节均匀分布）
        if per_level_targets is None:
            per_level_targets = {}
            for lvl in ['beginner', 'intermediate', 'advanced']:
                chapters = list(dist[lvl].keys())
                if not chapters:
                    continue
                uniform = 1.0 / len(chapters)
                per_level_targets[lvl] = {c: uniform for c in chapters}

        # 辅助：获取候选样本
        protected_rules = {'实验设计识别', '理论推导识别', '复杂分析识别', '高中范围外识别'}
        def chapter_of(item: ClassificationResult) -> str:
            feats = item.detailed_analysis.get('features', {}) if isinstance(item.detailed_analysis, dict) else {}
            return feats.get('primary_chapter', '') or '未识别'
        def adjustable(items: List[ClassificationResult]) -> List[ClassificationResult]:
            return [i for i in items if not any(rule in protected_rules for rule in i.matching_rules)]

        # 构建按级别与章节的索引
        by_level = {
            'beginner': adjustable([r for r in results if r.level == DifficultyLevel.BEGINNER]),
            'intermediate': adjustable([r for r in results if r.level == DifficultyLevel.INTERMEDIATE]),
            'advanced': adjustable([r for r in results if r.level == DifficultyLevel.ADVANCED])
        }

        # 计算目标计数
        totals = {lvl: len(by_level[lvl]) for lvl in by_level}
        target_counts = {}
        for lvl, targets in per_level_targets.items():
            level_total = totals.get(lvl, 0)
            target_counts[lvl] = {chap: int(round(level_total * ratio)) for chap, ratio in targets.items()}

        # 当前计数（基于 primary chapter）
        current_counts = {
            lvl: defaultdict(int) for lvl in ['beginner', 'intermediate', 'advanced']
        }
        for lvl, items in by_level.items():
            for it in items:
                current_counts[lvl][chapter_of(it)] += 1

        # 调整流程：对每个级别，若某章节不足，尝试从相邻级别迁移该章节的样本（低置信度优先）
        neighbors = {
            'beginner': ['intermediate'],
            'intermediate': ['beginner', 'advanced'],
            'advanced': ['intermediate']
        }

        # 按置信度排序，低置信度优先作为迁移候选
        for lvl in by_level:
            by_level[lvl].sort(key=lambda x: x.confidence)

        for lvl in ['beginner', 'intermediate', 'advanced']:
            if lvl not in target_counts:
                continue
            for chap, tgt in target_counts[lvl].items():
                cur = current_counts[lvl].get(chap, 0)
                while cur < tgt:
                    moved = False
                    for nb in neighbors[lvl]:
                        # 从邻级里寻找该章节的可迁移样本（最低置信度优先）
                        candidates = [it for it in by_level[nb] if chapter_of(it) == chap]
                        if not candidates:
                            continue
                        # 选择一个候选并迁移到当前级别
                        cand = candidates[0]
                        by_level[nb].remove(cand)
                        # 更新其级别
                        orig = cand.level
                        cand.level = DifficultyLevel[lvl.upper()]
                        # 更新计数
                        current_counts[lvl][chap] += 1
                        current_counts[nb][chap] -= 1
                        moved = True
                        cur += 1
                        # 在邻级中重新按置信度排序
                        by_level[nb].sort(key=lambda x: x.confidence)
                        break
                    if not moved:
                        break

        return results