# 高中化学结构化学分层作业设计

一个基于人工智能的高中化学结构化学作业智能分层系统，能够自动分析PDF格式的化学作业题目，根据难度进行智能分类，并生成适合不同层次学生的分层作业。

## 🎯 项目概述

本项目旨在解决高中化学教学中作业难度分层的问题，通过智能算法分析化学题目的复杂度，自动将题目分为基础、中级、高级三个层次，帮助教师更好地进行个性化教学。

### 核心功能

- **智能PDF处理**: 自动提取PDF中的化学题目和答案
- **多维度难度评估**: 基于化学专业词汇、计算步骤、概念深度等因素
- **三级分类系统**: 基础、中级、高级三个层次的智能分类
- **批量处理能力**: 支持同时处理多个PDF文件
- **格式保持**: 处理过程中保留原始文档格式
- **双接口支持**: 提供命令行和Web界面两种使用方式

## 🏗️ 技术架构

### 系统架构
```
chemistry-homework-classifier/
├── src/                          # 源代码目录
│   ├── pdf_processor/             # PDF处理模块
│   ├── difficulty_assessor/     # 难度评估模块
│   ├── classifier/                # 分类器模块
│   ├── output_generator/         # 输出生成器模块
│   ├── web_interface/            # Web界面模块
│   └── cli/                      # 命令行接口模块
├── tests/                         # 测试文件
├── examples/                      # 示例文件
├── docs/                          # 文档
├── data/                          # 数据文件
│   ├── chemistry_vocab/          # 化学词汇库
│   └── pdf_samples/             # PDF样本
└── requirements.txt               # 依赖包
```

### 技术栈

- **编程语言**: Python 3.8+
- **PDF处理**: PyPDF2, pdfplumber
- **Web框架**: Flask
- **机器学习**: scikit-learn, nltk
- **数据科学**: pandas, numpy
- **测试框架**: pytest
- **文档**: Sphinx

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- Git

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/your-username/chemistry-homework-classifier.git
cd chemistry-homework-classifier
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行测试**
```bash
pytest tests/
```

### 使用方法

#### 命令行界面

```bash
# 处理单个PDF文件
python -m src.cli.main --input path/to/homework.pdf --output classified/

# 批量处理多个PDF文件
python -m src.cli.main --input-dir path/to/pdfs/ --output-dir classified/

# 指定分类级别
python -m src.cli.main --input homework.pdf --levels basic,intermediate

# 自定义输出格式
python -m src.cli.main --input homework.pdf --format pdf --preserve-layout
```

#### Web界面

```bash
# 启动Web服务
python -m src.web_interface.app

# 访问Web界面
# 打开浏览器访问 http://localhost:5000
```

Web界面功能：
- 拖拽上传PDF文件
- 实时显示处理进度
- 预览分类结果
- 下载分层后的作业

## 📊 难度评估算法

### 评估维度

1. **文本复杂度分析**
   - 化学专业词汇密度
   - 句子长度和复杂度
   - 概念层次深度

2. **计算步骤评估**
   - 数学运算复杂度
   - 化学方程式数量
   - 推理步骤长度

3. **知识结构分析**
   - 涉及的概念数量
   - 概念间关联度
   - 创新思维要求

### 分类标准

#### 基础级别 (Basic)
- 基础概念理解
- 1-2步简单计算
- 单一知识点
- 标准解题模式

#### 中级级别 (Intermediate)
- 综合应用能力
- 3-5步中等计算
- 2-3个知识点结合
- 一定分析推理

#### 高级级别 (Advanced)
- 复杂分析能力
- 多步深度计算
- 跨章节综合
- 创新思维要求

## 📁 项目结构详解

### PDF处理模块 (`src/pdf_processor/`)
- `extractor.py`: PDF文本提取器
- `parser.py`: 题目和答案解析器
- `validator.py`: 格式验证器
- `batch_processor.py`: 批量处理器

### 难度评估模块 (`src/difficulty_assessor/`)
- `vocab_analyzer.py`: 词汇复杂度分析
- `step_calculator.py`: 计算步骤评估
- `concept_depth.py`: 概念深度评估
- `scoring_engine.py`: 综合评分引擎

### 分类器模块 (`src/classifier/`)
- `rule_engine.py`: 分类规则引擎
- `ml_classifier.py`: 机器学习分类器
- `validator.py`: 分类结果验证
- `config.py`: 分类配置

### 输出生成器模块 (`src/output_generator/`)
- `pdf_generator.py`: PDF文件生成器
- `layout_preserver.py`: 布局保持器
- `label_adder.py`: 分层标识添加器
- `organizer.py`: 题目重新排序器

## 🧪 测试

### 单元测试
```bash
# 运行所有单元测试
pytest tests/unit/

# 运行特定模块测试
pytest tests/unit/test_pdf_processor.py
pytest tests/unit/test_difficulty_assessor.py
```

### 集成测试
```bash
# 运行集成测试
pytest tests/integration/
```

### 端到端测试
```bash
# 运行端到端测试
pytest tests/e2e/
```

## 📈 性能指标

### 分类准确率
- 基础题目识别率: ≥95%
- 中级题目识别率: ≥90%
- 高级题目识别率: ≥85%

### 处理速度
- 单页PDF处理时间: <2秒
- 批量处理速度: >10页/分钟

### 系统稳定性
- 内存使用: <500MB
- CPU占用: <30%
- 崩溃率: <0.1%

## 🔧 配置选项

### 分类参数配置
```yaml
# config/classification.yaml
classification:
  basic:
    max_steps: 2
    max_concepts: 1
    vocab_threshold: 0.3
  
  intermediate:
    max_steps: 5
    max_concepts: 3
    vocab_threshold: 0.6
  
  advanced:
    min_steps: 6
    min_concepts: 4
    vocab_threshold: 0.8
```

### 词汇库配置
```yaml
# config/vocabulary.yaml
chemistry_terms:
  basic: ["原子", "分子", "元素", "化合物"]
  intermediate: ["化学键", "晶体结构", "配位数"]
  advanced: ["杂化轨道", "分子轨道", "晶体场理论"]
```

## 🤝 贡献指南

### 开发环境设置
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

### 代码规范
- 遵循 PEP 8 Python 编码规范
- 添加适当的注释和文档字符串
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢所有贡献者的努力
- 感谢开源社区的支持
- 特别感谢化学教育专家的指导

## 📞 联系方式

- 项目维护者: [Your Name](mailto:your.email@example.com)
- 项目主页: https://github.com/your-username/chemistry-homework-classifier
- 问题反馈: https://github.com/your-username/chemistry-homework-classifier/issues

## 📚 相关资源

- [化学教育技术标准](docs/education_standards.md)
- [算法详细文档](docs/algorithms.md)
- [API文档](docs/api.md)
- [用户手册](docs/user_manual.md)

---

⭐ 如果这个项目对你有帮助，请给个星标支持一下！