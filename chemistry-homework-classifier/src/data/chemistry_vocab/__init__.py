"""
化学词汇数据包的初始化模块
整合词汇和概念数据库
"""

from .vocabulary import ChemistryVocabulary
from .concepts import ChemistryConcepts

__all__ = ['ChemistryVocabulary', 'ChemistryConcepts']