import os
import sys
from pathlib import Path

# 将子项目的 src 加入 sys.path 以便导入
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUBPROJECT_SRC = PROJECT_ROOT / 'chemistry-homework-classifier' / 'src'
sys.path.insert(0, str(SUBPROJECT_SRC))

from difficulty_assessor.classifier import ThreeTierClassifier, DifficultyLevel


def test_beginner_classification_high_school_scope():
    clf = ThreeTierClassifier()
    q = (
        "简述元素周期律的基本内容，并说明周期表中原子半径的变化趋势。"
        "请给出典型元素的例子进行说明。"
    )
    result = clf.classify_question(q)
    assert result.level == DifficultyLevel.BEGINNER, (
        f"Expected BEGINNER, got {result.level} with reasons {result.reasons}"
    )


def test_intermediate_classification_comprehensive_application():
    clf = ThreeTierClassifier()
    q = (
        "分析化学平衡的移动方向，给出相应的反应方程式并计算平衡常数。"
        "讨论温度与压强对平衡的影响，并比较不同条件下的转化率。"
    )
    result = clf.classify_question(q)
    assert result.level == DifficultyLevel.INTERMEDIATE, (
        f"Expected INTERMEDIATE, got {result.level} with reasons {result.reasons}"
    )


def test_advanced_out_of_scope_detection():
    clf = ThreeTierClassifier()
    q = (
        "使用DFT方法和分子轨道理论分析苯分子的电子能带结构，"
        "并结合NMR谱解释取代基的定位效应。"
    )
    result = clf.classify_question(q)
    assert result.level == DifficultyLevel.ADVANCED, (
        f"Expected ADVANCED, got {result.level} with reasons {result.reasons}"
    )
    assert any('高中范围外识别' in rule for rule in result.matching_rules), (
        f"Expected out-of-scope rule match, got {result.matching_rules}"
    )