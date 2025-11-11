"""
化学概念和公式数据库
用于题目深度分析和难度评估
"""

import json
import logging
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class ChemistryConcepts:
    """化学概念和公式管理类"""
    
    def __init__(self, concepts_file: str = None):
        """
        初始化化学概念库
        
        Args:
            concepts_file: 概念文件路径，如果为None则使用默认概念
        """
        self.concepts_file = concepts_file or self._get_default_concepts_path()
        self.concepts = {}
        self.formulas = {}
        self.reactions = {}
        self.theories = {}
        self._load_concepts()
    
    def _get_default_concepts_path(self) -> str:
        """获取默认概念文件路径"""
        current_dir = Path(__file__).parent
        return str(current_dir / "chemistry_concepts.json")
    
    def _load_concepts(self):
        """加载化学概念库"""
        try:
            if Path(self.concepts_file).exists():
                with open(self.concepts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.concepts = data.get('concepts', {})
                    self.formulas = data.get('formulas', {})
                    self.reactions = data.get('reactions', {})
                    self.theories = data.get('theories', {})
                logger.info(f"化学概念库加载成功: {len(self.concepts)} 个概念")
            else:
                logger.info("概念文件不存在，创建默认概念库")
                self._create_default_concepts()
                self.save_concepts()
        except Exception as e:
            logger.error(f"化学概念库加载失败: {str(e)}")
            self._create_default_concepts()
    
    def _create_default_concepts(self):
        """创建默认化学概念库"""
        # 基础概念 (难度1-2)
        self.concepts = {
            '原子结构基础': {
                'level': 1,
                'description': '原子由原子核和核外电子组成',
                'key_points': ['原子核', '电子', '质子', '中子'],
                'prerequisites': [],
                'applications': ['元素周期表', '化学键']
            },
            '元素周期律': {
                'level': 2,
                'description': '元素性质随原子序数递增而呈周期性变化',
                'key_points': ['周期', '族', '原子半径', '电离能'],
                'prerequisites': ['原子结构基础'],
                'applications': ['元素性质预测', '化学反应']
            },
            '化学键': {
                'level': 2,
                'description': '原子间通过电子相互作用形成的结合力',
                'key_points': ['离子键', '共价键', '金属键', '氢键'],
                'prerequisites': ['原子结构基础'],
                'applications': ['分子结构', '晶体结构']
            },
            '分子间作用力': {
                'level': 2,
                'description': '分子间的相互作用力',
                'key_points': ['范德华力', '氢键', '偶极-偶极作用'],
                'prerequisites': ['化学键'],
                'applications': ['物质性质', '溶解性']
            }
        }
        
        # 结构化学概念 (难度3-5)
        structural_concepts = {
            '价层电子对互斥理论': {
                'level': 4,
                'description': '通过价层电子对的排斥作用预测分子几何构型',
                'key_points': ['价层电子对', '排斥作用', '分子构型', '孤对电子'],
                'prerequisites': ['原子结构基础', '化学键'],
                'applications': ['分子形状预测', '键角分析']
            },
            '杂化轨道理论': {
                'level': 4,
                'description': '原子轨道重新组合形成杂化轨道',
                'key_points': ['sp杂化', 'sp2杂化', 'sp3杂化', '杂化类型'],
                'prerequisites': ['原子结构基础', '原子轨道'],
                'applications': ['分子结构', '化学键解释']
            },
            '分子轨道理论': {
                'level': 5,
                'description': '分子轨道由原子轨道线性组合而成',
                'key_points': ['成键轨道', '反键轨道', '分子轨道', '能级图'],
                'prerequisites': ['原子轨道', '量子力学基础'],
                'applications': ['分子稳定性', '光谱性质']
            },
            '晶体场理论': {
                'level': 5,
                'description': '配体场对中心金属离子d轨道的影响',
                'key_points': ['晶体场分裂', 'd轨道', '配体场', '高自旋低自旋'],
                'prerequisites': ['原子轨道', '配位化学'],
                'applications': ['配合物性质', '颜色解释']
            }
        }
        
        # 有机化学概念 (难度3-5)
        organic_concepts = {
            '同分异构': {
                'level': 3,
                'description': '分子式相同但结构不同的化合物',
                'key_points': ['结构异构', '立体异构', '构型', '构象'],
                'prerequisites': ['分子结构'],
                'applications': ['有机化合物分类', '性质预测']
            },
            '手性': {
                'level': 5,
                'description': '分子不具有对称中心或对称面，不能与其镜像重合',
                'key_points': ['手性中心', '对映体', '非对映体', '旋光性'],
                'prerequisites': ['立体化学'],
                'applications': ['药物化学', '生物活性']
            },
            '芳香性': {
                'level': 4,
                'description': '具有特殊稳定性的环状共轭体系',
                'key_points': ['休克尔规则', '芳香性', '反芳香性', '非芳香性'],
                'prerequisites': ['共轭体系', '分子轨道'],
                'applications': ['芳香化合物', '反应机理']
            }
        }
        
        self.concepts.update(structural_concepts)
        self.concepts.update(organic_concepts)
        
        # 化学公式
        self.formulas = {
            '理想气体状态方程': {
                'formula': 'PV = nRT',
                'level': 2,
                'variables': {'P': '压力', 'V': '体积', 'n': '物质的量', 'R': '气体常数', 'T': '温度'},
                'conditions': ['理想气体', '平衡态'],
                'applications': ['气体计算', '状态变化']
            },
            '化学反应速率': {
                'formula': 'v = k[A]^m[B]^n',
                'level': 3,
                'variables': {'v': '反应速率', 'k': '速率常数', '[A],[B]': '反应物浓度', 'm,n': '反应级数'},
                'conditions': ['恒温', '均相反应'],
                'applications': ['反应动力学', '机理研究']
            },
            '能斯特方程': {
                'formula': 'E = E° - (RT/nF)lnQ',
                'level': 5,
                'variables': {'E': '电极电势', 'E°': '标准电极电势', 'R': '气体常数', 'T': '温度', 'n': '电子数', 'F': '法拉第常数', 'Q': '反应商'},
                'conditions': ['电化学平衡', '可逆电极'],
                'applications': ['电极电势计算', '电池电动势']
            },
            '阿伦尼乌斯方程': {
                'formula': 'k = Ae^(-Ea/RT)',
                'level': 4,
                'variables': {'k': '速率常数', 'A': '指前因子', 'Ea': '活化能', 'R': '气体常数', 'T': '温度'},
                'conditions': ['基元反应', '温度范围适用'],
                'applications': ['速率常数计算', '活化能测定']
            }
        }
        
        # 化学反应类型
        self.reactions = {
            '酸碱中和反应': {
                'level': 1,
                'general_form': '酸 + 碱 → 盐 + 水',
                'examples': ['HCl + NaOH → NaCl + H2O'],
                'characteristics': ['放热', '离子反应'],
                'applications': ['滴定分析', 'pH调节']
            },
            '氧化还原反应': {
                'level': 3,
                'general_form': '氧化剂 + 还原剂 → 氧化产物 + 还原产物',
                'examples': ['CuO + H2 → Cu + H2O'],
                'characteristics': ['电子转移', '化合价变化'],
                'applications': ['电化学', '腐蚀防护']
            },
            '配位反应': {
                'level': 4,
                'general_form': '中心离子 + 配体 → 配合物',
                'examples': ['Cu2+ + 4NH3 → [Cu(NH3)4]2+'],
                'characteristics': ['配位键形成', '几何构型'],
                'applications': ['分析化学', '催化剂']
            }
        }
        
        # 化学理论
        self.theories = {
            '原子结构理论': {
                'level': 3,
                'description': '描述原子内部结构和电子排布的理论',
                'key_principles': ['量子化', '波粒二象性', '不确定性原理'],
                'mathematical_basis': ['薛定谔方程', '波函数'],
                'applications': ['元素周期律', '化学键理论']
            },
            '化学键理论': {
                'level': 3,
                'description': '解释原子间相互作用和分子形成的理论',
                'key_principles': ['电子共享', '电子转移', '轨道重叠'],
                'mathematical_basis': ['分子轨道理论', '价键理论'],
                'applications': ['分子结构', '反应机理']
            },
            '化学平衡理论': {
                'level': 3,
                'description': '描述可逆反应达到平衡状态的理论',
                'key_principles': ['动态平衡', '勒沙特列原理', '平衡常数'],
                'mathematical_basis': ['平衡常数表达式', '反应商'],
                'applications': ['工艺优化', '产率计算']
            }
        }
    
    def analyze_concept_depth(self, text: str) -> Dict[str, any]:
        """
        分析文本中的化学概念深度
        
        Args:
            text: 输入文本
            
        Returns:
            概念深度分析结果
        """
        if not text:
            return {
                'total_concepts': 0,
                'concept_levels': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
                'average_level': 0.0,
                'max_level': 0,
                'found_concepts': [],
                'prerequisites_missing': [],
                'concept_score': 0.0
            }
        
        found_concepts = []
        concept_levels = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        total_level = 0
        max_level = 0
        
        # 搜索概念
        for concept_name, concept_info in self.concepts.items():
            if concept_name in text:
                level = concept_info['level']
                found_concepts.append({
                    'concept': concept_name,
                    'level': level,
                    'description': concept_info['description'],
                    'key_points': concept_info['key_points']
                })
                concept_levels[str(level)] += 1
                total_level += level
                max_level = max(max_level, level)
        
        # 搜索公式
        for formula_name, formula_info in self.formulas.items():
            if formula_name in text or formula_info['formula'] in text:
                level = formula_info['level']
                found_concepts.append({
                    'concept': formula_name,
                    'level': level,
                    'formula': formula_info['formula'],
                    'variables': formula_info['variables']
                })
                concept_levels[str(level)] += 1
                total_level += level
                max_level = max(max_level, level)
        
        # 搜索反应类型
        for reaction_name, reaction_info in self.reactions.items():
            if reaction_name in text:
                level = reaction_info['level']
                found_concepts.append({
                    'concept': reaction_name,
                    'level': level,
                    'general_form': reaction_info['general_form'],
                    'characteristics': reaction_info['characteristics']
                })
                concept_levels[str(level)] += 1
                total_level += level
                max_level = max(max_level, level)
        
        total_concepts = len(found_concepts)
        average_level = total_level / total_concepts if total_concepts > 0 else 0
        
        # 检查先修知识
        prerequisites_missing = []
        for concept in found_concepts:
            concept_name = concept['concept']
            if concept_name in self.concepts:
                prereqs = self.concepts[concept_name]['prerequisites']
                for prereq in prereqs:
                    if not any(fc['concept'] == prereq for fc in found_concepts):
                        prerequisites_missing.append({
                            'concept': concept_name,
                            'missing_prerequisite': prereq
                        })
        
        # 计算概念深度分数
        concept_score = self._calculate_concept_score(
            total_concepts, average_level, max_level, len(prerequisites_missing)
        )
        
        return {
            'total_concepts': total_concepts,
            'concept_levels': concept_levels,
            'average_level': average_level,
            'max_level': max_level,
            'found_concepts': found_concepts,
            'prerequisites_missing': prerequisites_missing,
            'concept_score': concept_score
        }
    
    def _calculate_concept_score(self, total_concepts: int, avg_level: float, 
                               max_level: int, missing_prereqs: int) -> float:
        """计算概念深度分数"""
        # 概念数量分数 (0-30分)
        concept_count_score = min(total_concepts * 3, 30)
        
        # 平均深度分数 (0-25分)
        avg_level_score = min(avg_level * 5, 25)
        
        # 最大深度分数 (0-25分)
        max_level_score = min(max_level * 5, 25)
        
        # 先修知识扣分 (最多扣20分)
        prereq_penalty = min(missing_prereqs * 4, 20)
        
        total_score = concept_count_score + avg_level_score + max_level_score - prereq_penalty
        return max(0, min(total_score, 100))
    
    def get_concept_info(self, concept_name: str) -> Optional[Dict[str, any]]:
        """
        获取特定概念的详细信息
        
        Args:
            concept_name: 概念名称
            
        Returns:
            概念信息或None
        """
        if concept_name in self.concepts:
            info = self.concepts[concept_name].copy()
            info['type'] = 'concept'
            return info
        elif concept_name in self.formulas:
            info = self.formulas[concept_name].copy()
            info['type'] = 'formula'
            return info
        elif concept_name in self.reactions:
            info = self.reactions[concept_name].copy()
            info['type'] = 'reaction'
            return info
        elif concept_name in self.theories:
            info = self.theories[concept_name].copy()
            info['type'] = 'theory'
            return info
        
        return None
    
    def get_prerequisites(self, concept_name: str) -> List[str]:
        """
        获取概念的先修知识
        
        Args:
            concept_name: 概念名称
            
        Returns:
            先修知识列表
        """
        if concept_name in self.concepts:
            return self.concepts[concept_name]['prerequisites'].copy()
        return []
    
    def get_applications(self, concept_name: str) -> List[str]:
        """
        获取概念的应用领域
        
        Args:
            concept_name: 概念名称
            
        Returns:
            应用领域列表
        """
        if concept_name in self.concepts:
            return self.concepts[concept_name]['applications'].copy()
        return []
    
    def get_concepts_by_level(self, level: int) -> List[str]:
        """
        获取指定难度级别的概念
        
        Args:
            level: 难度级别 (1-5)
            
        Returns:
            概念名称列表
        """
        concepts = []
        for name, info in self.concepts.items():
            if info['level'] == level:
                concepts.append(name)
        return concepts
    
    def add_concept(self, name: str, level: int, description: str, 
                   key_points: List[str], prerequisites: List[str], 
                   applications: List[str], save: bool = True):
        """
        添加新概念
        
        Args:
            name: 概念名称
            level: 难度级别
            description: 概念描述
            key_points: 关键要点
            prerequisites: 先修知识
            applications: 应用领域
            save: 是否保存到文件
        """
        self.concepts[name] = {
            'level': level,
            'description': description,
            'key_points': key_points,
            'prerequisites': prerequisites,
            'applications': applications
        }
        
        if save:
            self.save_concepts()
        
        logger.info(f"添加新概念: {name} (级别: {level})")
    
    def add_formula(self, name: str, formula: str, level: int, 
                   variables: Dict[str, str], conditions: List[str], 
                   applications: List[str], save: bool = True):
        """
        添加新公式
        
        Args:
            name: 公式名称
            formula: 数学表达式
            level: 难度级别
            variables: 变量说明
            conditions: 适用条件
            applications: 应用领域
            save: 是否保存到文件
        """
        self.formulas[name] = {
            'formula': formula,
            'level': level,
            'variables': variables,
            'conditions': conditions,
            'applications': applications
        }
        
        if save:
            self.save_concepts()
        
        logger.info(f"添加新公式: {name} (级别: {level})")
    
    def save_concepts(self):
        """保存概念库到文件"""
        try:
            data = {
                'concepts': self.concepts,
                'formulas': self.formulas,
                'reactions': self.reactions,
                'theories': self.theories,
                'metadata': {
                    'version': '1.0',
                    'total_concepts': len(self.concepts),
                    'total_formulas': len(self.formulas),
                    'total_reactions': len(self.reactions),
                    'total_theories': len(self.theories)
                }
            }
            
            with open(self.concepts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"化学概念库保存成功: {self.concepts_file}")
            
        except Exception as e:
            logger.error(f"化学概念库保存失败: {str(e)}")
    
    def get_statistics(self) -> Dict[str, any]:
        """获取概念库统计信息"""
        concept_levels = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        for info in self.concepts.values():
            concept_levels[str(info['level'])] += 1
        
        formula_levels = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        for info in self.formulas.values():
            formula_levels[str(info['level'])] += 1
        
        return {
            'total_concepts': len(self.concepts),
            'total_formulas': len(self.formulas),
            'total_reactions': len(self.reactions),
            'total_theories': len(self.theories),
            'concept_level_distribution': concept_levels,
            'formula_level_distribution': formula_levels,
            'avg_concept_level': sum(info['level'] for info in self.concepts.values()) / len(self.concepts) if self.concepts else 0,
            'avg_formula_level': sum(info['level'] for info in self.formulas.values()) / len(self.formulas) if self.formulas else 0
        }