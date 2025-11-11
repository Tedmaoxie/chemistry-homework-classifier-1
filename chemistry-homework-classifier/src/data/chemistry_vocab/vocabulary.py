"""
化学专业词汇数据库
用于题目复杂度分析和难度评估
"""

import json
import logging
from typing import Dict, List, Set, Tuple
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class ChemistryVocabulary:
    """化学专业词汇管理类"""
    
    def __init__(self, vocab_file: str = None):
        """
        初始化词汇库
        
        Args:
            vocab_file: 词汇文件路径，如果为None则使用默认词汇
        """
        self.vocab_file = vocab_file or self._get_default_vocab_path()
        self.vocabulary = {}
        self.categorized_vocab = defaultdict(set)
        self.complexity_scores = {}
        self._load_vocabulary()
    
    def _get_default_vocab_path(self) -> str:
        """获取默认词汇文件路径"""
        current_dir = Path(__file__).parent
        return str(current_dir / "chemistry_vocab.json")
    
    def _load_vocabulary(self):
        """加载词汇库"""
        try:
            if Path(self.vocab_file).exists():
                with open(self.vocab_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.vocabulary = data.get('vocabulary', {})
                    self.complexity_scores = data.get('complexity_scores', {})
                    self._build_categorized_vocab()
                logger.info(f"词汇库加载成功: {len(self.vocabulary)} 个词汇")
            else:
                logger.info("词汇文件不存在，创建默认词汇库")
                self._create_default_vocabulary()
                self.save_vocabulary()
        except Exception as e:
            logger.error(f"词汇库加载失败: {str(e)}")
            self._create_default_vocabulary()
    
    def _create_default_vocabulary(self):
        """创建默认化学词汇库"""
        # 基础概念词汇（难度1-2）
        basic_concepts = {
            '原子': 1, '分子': 1, '元素': 1, '化合物': 1, '混合物': 1,
            '化学式': 1, '分子式': 1, '结构式': 2, '电子式': 2, '化合价': 2,
            '相对原子质量': 2, '相对分子质量': 2, '摩尔质量': 2, '物质的量': 2,
            '阿伏伽德罗常数': 2, '摩尔': 1, '气体摩尔体积': 2, '溶液': 1,
            '溶质': 1, '溶剂': 1, '浓度': 1, '质量分数': 2, '物质的量浓度': 2
        }
        
        # 化学反应词汇（难度2-3）
        reaction_terms = {
            '化学反应': 1, '化学方程式': 2, '离子方程式': 3, '热化学方程式': 3,
            '氧化还原反应': 3, '置换反应': 2, '复分解反应': 2, '化合反应': 1,
            '分解反应': 1, '中和反应': 2, '沉淀反应': 2, '气体生成反应': 2,
            '氧化剂': 2, '还原剂': 2, '氧化产物': 3, '还原产物': 3,
            '电子转移': 3, '电荷守恒': 3, '质量守恒': 2, '能量守恒': 3
        }
        
        # 结构化学词汇（难度3-4）
        structural_chemistry = {
            '原子结构': 2, '电子云': 3, '原子轨道': 4, '电子排布': 3,
            '能级': 3, '能层': 3, '价电子': 2, '价层电子对互斥理论': 4,
            '杂化轨道理论': 4, '分子轨道理论': 5, '共价键': 2, '离子键': 2,
            '金属键': 2, '氢键': 3, '范德华力': 3, '分子间作用力': 3,
            '晶体结构': 3, '晶胞': 4, '晶格': 4, '配位数': 3, '晶系': 4,
            '空间点阵': 5, '对称性': 4, '空间群': 5, 'X射线衍射': 5
        }
        
        # 有机化学词汇（难度3-5）
        organic_chemistry = {
            '有机化合物': 2, '烃': 2, '烷烃': 2, '烯烃': 3, '炔烃': 3,
            '芳香烃': 3, '苯': 2, '甲苯': 3, '官能团': 3, '同分异构': 4,
            '结构异构': 3, '立体异构': 5, '手性': 5, '手性中心': 5,
            '对映异构': 5, '非对映异构': 5, '旋光性': 4, '比旋光度': 4,
            '亲核取代': 4, '亲电取代': 4, '加成反应': 3, '消除反应': 4,
            '重排反应': 5, '周环反应': 5, '狄尔斯-阿尔德反应': 5
        }
        
        # 分析化学词汇（难度2-4）
        analytical_chemistry = {
            '定性分析': 2, '定量分析': 2, '滴定': 2, '酸碱滴定': 3,
            '氧化还原滴定': 3, '络合滴定': 4, '沉淀滴定': 3, '指示剂': 2,
            '滴定终点': 3, '等当点': 3, '缓冲溶液': 3, 'pH值': 2,
            '分光光度法': 4, '原子吸收光谱': 4, '红外光谱': 4, '核磁共振': 5,
            '质谱': 5, '色谱': 4, '气相色谱': 4, '液相色谱': 4
        }
        
        # 物理化学词汇（难度3-5）
        physical_chemistry = {
            '化学热力学': 4, '焓': 3, '熵': 4, '吉布斯自由能': 4,
            '化学平衡': 3, '平衡常数': 3, '勒沙特列原理': 4, '反应速率': 3,
            '速率常数': 3, '活化能': 4, '阿伦尼乌斯方程': 4, '反应级数': 4,
            '催化': 3, '催化剂': 3, '电化学': 4, '电极电势': 4,
            '能斯特方程': 5, '法拉第定律': 4, '电解质': 2, '电离': 3
        }
        
        # 合并所有词汇
        self.vocabulary.update(basic_concepts)
        self.vocabulary.update(reaction_terms)
        self.vocabulary.update(structural_chemistry)
        self.vocabulary.update(organic_chemistry)
        self.vocabulary.update(analytical_chemistry)
        self.vocabulary.update(physical_chemistry)
        
        # 设置复杂度分数
        self.complexity_scores = self.vocabulary.copy()
        
        # 构建分类词汇
        self._build_categorized_vocab()
        
        logger.info(f"默认词汇库创建完成: {len(self.vocabulary)} 个词汇")
    
    def _build_categorized_vocab(self):
        """构建分类词汇索引"""
        self.categorized_vocab.clear()
        
        # 按难度分类
        for word, score in self.complexity_scores.items():
            if score <= 2:
                self.categorized_vocab['basic'].add(word)
            elif score <= 3:
                self.categorized_vocab['intermediate'].add(word)
            elif score <= 4:
                self.categorized_vocab['advanced'].add(word)
            else:
                self.categorized_vocab['expert'].add(word)
        
        # 按主题分类（基于关键词匹配）
        structural_keywords = ['结构', '轨道', '晶体', '键', '能级', '晶胞']
        organic_keywords = ['有机', '烃', '苯', '官能团', '异构', '反应']
        analytical_keywords = ['分析', '滴定', '光谱', '色谱', '质谱']
        physical_keywords = ['热力学', '平衡', '动力学', '电化学', '焓', '熵']
        
        for word in self.vocabulary:
            if any(keyword in word for keyword in structural_keywords):
                self.categorized_vocab['structural'].add(word)
            if any(keyword in word for keyword in organic_keywords):
                self.categorized_vocab['organic'].add(word)
            if any(keyword in word for keyword in analytical_keywords):
                self.categorized_vocab['analytical'].add(word)
            if any(keyword in word for keyword in physical_keywords):
                self.categorized_vocab['physical'].add(word)
    
    def analyze_text_complexity(self, text: str) -> Dict[str, any]:
        """
        分析文本化学复杂度
        
        Args:
            text: 输入文本
            
        Returns:
            复杂度分析结果
        """
        if not text:
            return {
                'total_words': 0,
                'chemistry_words': 0,
                'chemistry_ratio': 0.0,
                'average_complexity': 0.0,
                'max_complexity': 0,
                'complexity_distribution': {'basic': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0},
                'found_words': [],
                'complexity_score': 0.0
            }
        
        # 文本预处理
        import re
        # 移除标点符号和数字，保留中文和英文
        clean_text = re.sub(r'[^\u4e00-\u9fff\u4e00-\u9fa5a-zA-Z\s]', ' ', text)
        words = clean_text.split()
        
        total_words = len(words)
        chemistry_words = 0
        complexity_sum = 0
        max_complexity = 0
        complexity_dist = {'basic': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0}
        found_words = []
        
        # 分析每个词汇
        for word in words:
            word = word.strip()
            if not word:
                continue
            
            # 检查是否在化学词汇库中
            if word in self.vocabulary:
                chemistry_words += 1
                complexity = self.complexity_scores.get(word, 1)
                complexity_sum += complexity
                max_complexity = max(max_complexity, complexity)
                
                # 复杂度分布
                if complexity <= 2:
                    complexity_dist['basic'] += 1
                elif complexity <= 3:
                    complexity_dist['intermediate'] += 1
                elif complexity <= 4:
                    complexity_dist['advanced'] += 1
                else:
                    complexity_dist['expert'] += 1
                
                found_words.append({
                    'word': word,
                    'complexity': complexity,
                    'category': self._get_complexity_category(complexity)
                })
        
        # 计算平均复杂度
        average_complexity = complexity_sum / chemistry_words if chemistry_words > 0 else 0
        
        # 计算综合复杂度分数（考虑词汇密度和平均复杂度）
        chemistry_ratio = chemistry_words / total_words if total_words > 0 else 0
        complexity_score = self._calculate_complexity_score(
            chemistry_ratio, average_complexity, max_complexity, chemistry_words
        )
        
        return {
            'total_words': total_words,
            'chemistry_words': chemistry_words,
            'chemistry_ratio': chemistry_ratio,
            'average_complexity': average_complexity,
            'max_complexity': max_complexity,
            'complexity_distribution': complexity_dist,
            'found_words': found_words,
            'complexity_score': complexity_score
        }
    
    def _get_complexity_category(self, complexity: int) -> str:
        """获取复杂度类别"""
        if complexity <= 2:
            return 'basic'
        elif complexity <= 3:
            return 'intermediate'
        elif complexity <= 4:
            return 'advanced'
        else:
            return 'expert'
    
    def _calculate_complexity_score(self, ratio: float, avg_complexity: float, 
                                 max_complexity: float, word_count: int) -> float:
        """计算综合复杂度分数"""
        # 基础分数：化学词汇占比（0-40分）
        ratio_score = min(ratio * 100, 40)
        
        # 平均复杂度分数（0-30分）
        avg_score = min(avg_complexity * 6, 30)
        
        # 最大复杂度分数（0-20分）
        max_score = min(max_complexity * 4, 20)
        
        # 词汇数量分数（0-10分）
        count_score = min(word_count * 0.5, 10)
        
        total_score = ratio_score + avg_score + max_score + count_score
        return min(total_score, 100)
    
    def get_vocabulary_by_category(self, category: str) -> Set[str]:
        """
        获取指定类别的词汇
        
        Args:
            category: 类别名称 (basic, intermediate, advanced, expert, structural, organic, analytical, physical)
            
        Returns:
            词汇集合
        """
        return self.categorized_vocab.get(category, set()).copy()
    
    def add_vocabulary(self, word: str, complexity: int, save: bool = True):
        """
        添加新词汇
        
        Args:
            word: 词汇
            complexity: 复杂度分数 (1-5)
            save: 是否保存到文件
        """
        self.vocabulary[word] = complexity
        self.complexity_scores[word] = complexity
        self._build_categorized_vocab()
        
        if save:
            self.save_vocabulary()
        
        logger.info(f"添加新词汇: {word} (复杂度: {complexity})")
    
    def remove_vocabulary(self, word: str, save: bool = True):
        """
        移除词汇
        
        Args:
            word: 词汇
            save: 是否保存到文件
        """
        if word in self.vocabulary:
            del self.vocabulary[word]
            del self.complexity_scores[word]
            self._build_categorized_vocab()
            
            if save:
                self.save_vocabulary()
            
            logger.info(f"移除词汇: {word}")
    
    def update_vocabulary(self, word: str, complexity: int, save: bool = True):
        """
        更新词汇复杂度
        
        Args:
            word: 词汇
            complexity: 新复杂度分数
            save: 是否保存到文件
        """
        if word in self.vocabulary:
            self.vocabulary[word] = complexity
            self.complexity_scores[word] = complexity
            self._build_categorized_vocab()
            
            if save:
                self.save_vocabulary()
            
            logger.info(f"更新词汇复杂度: {word} -> {complexity}")
    
    def save_vocabulary(self):
        """保存词汇库到文件"""
        try:
            data = {
                'vocabulary': self.vocabulary,
                'complexity_scores': self.complexity_scores,
                'metadata': {
                    'version': '1.0',
                    'total_words': len(self.vocabulary),
                    'categories': list(self.categorized_vocab.keys()),
                    'last_updated': str(pd.Timestamp.now()) if 'pd' in globals() else 'unknown'
                }
            }
            
            with open(self.vocab_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"词汇库保存成功: {self.vocab_file}")
            
        except Exception as e:
            logger.error(f"词汇库保存失败: {str(e)}")
    
    def get_statistics(self) -> Dict[str, any]:
        """获取词汇库统计信息"""
        stats = {
            'total_words': len(self.vocabulary),
            'avg_complexity': sum(self.complexity_scores.values()) / len(self.complexity_scores) if self.complexity_scores else 0,
            'complexity_distribution': {
                'basic': len(self.categorized_vocab['basic']),
                'intermediate': len(self.categorized_vocab['intermediate']),
                'advanced': len(self.categorized_vocab['advanced']),
                'expert': len(self.categorized_vocab['expert'])
            },
            'topic_distribution': {
                'structural': len(self.categorized_vocab['structural']),
                'organic': len(self.categorized_vocab['organic']),
                'analytical': len(self.categorized_vocab['analytical']),
                'physical': len(self.categorized_vocab['physical'])
            }
        }
        return stats
    
    def search_vocabulary(self, keyword: str, category: str = None) -> List[Tuple[str, int]]:
        """
        搜索词汇
        
        Args:
            keyword: 搜索关键词
            category: 指定类别（可选）
            
        Returns:
            匹配的词汇列表 (词汇, 复杂度)
        """
        results = []
        
        # 确定搜索范围
        search_vocab = self.vocabulary
        if category and category in self.categorized_vocab:
            search_vocab = {word: self.vocabulary[word] for word in self.categorized_vocab[category]}
        
        # 搜索匹配
        for word, complexity in search_vocab.items():
            if keyword.lower() in word.lower():
                results.append((word, complexity))
        
        # 按复杂度排序
        results.sort(key=lambda x: x[1])
        return results
    
    def export_vocabulary(self, output_file: str, format: str = 'json'):
        """
        导出词汇库
        
        Args:
            output_file: 输出文件路径
            format: 导出格式 (json, csv, txt)
        """
        try:
            if format.lower() == 'json':
                self._export_json(output_file)
            elif format.lower() == 'csv':
                self._export_csv(output_file)
            elif format.lower() == 'txt':
                self._export_txt(output_file)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            
            logger.info(f"词汇库导出成功: {output_file} (格式: {format})")
            
        except Exception as e:
            logger.error(f"词汇库导出失败: {str(e)}")
    
    def _export_json(self, output_file: str):
        """导出为JSON格式"""
        data = {
            'vocabulary': self.vocabulary,
            'complexity_scores': self.complexity_scores,
            'statistics': self.get_statistics()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _export_csv(self, output_file: str):
        """导出为CSV格式"""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['词汇', '复杂度', '类别'])
            
            for word, complexity in sorted(self.vocabulary.items(), key=lambda x: x[1]):
                category = self._get_complexity_category(complexity)
                writer.writerow([word, complexity, category])
    
    def _export_txt(self, output_file: str):
        """导出为TXT格式"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("化学专业词汇库\n")
            f.write("=" * 50 + "\n\n")
            
            # 按复杂度分组
            for category in ['basic', 'intermediate', 'advanced', 'expert']:
                f.write(f"\n{self._get_category_name(category)} (复杂度 {self._get_category_range(category)}):\n")
                f.write("-" * 30 + "\n")
                
                words = sorted(list(self.categorized_vocab[category]))
                for word in words:
                    complexity = self.complexity_scores[word]
                    f.write(f"  {word:<20} (复杂度: {complexity})\n")
    
    def _get_category_name(self, category: str) -> str:
        """获取类别中文名称"""
        names = {
            'basic': '基础词汇',
            'intermediate': '中级词汇',
            'advanced': '高级词汇',
            'expert': '专家级词汇'
        }
        return names.get(category, category)
    
    def _get_category_range(self, category: str) -> str:
        """获取类别复杂度范围"""
        ranges = {
            'basic': '1-2',
            'intermediate': '3',
            'advanced': '4',
            'expert': '5'
        }
        return ranges.get(category, '未知')