# Chemistry Homework Classifier – Web & CLI

一个用于化学题目难度评估与报表生成的工具集，含命令行与 Flask Web 界面。

- 按综合难度 `total_score` 降序排序生成报告（PDF / DOCX）。
- 支持 TXT / PDF / DOCX 输入（自动提取文本）。
- 报告包含封面、统计信息、题目详情与评分维度说明。
- Web 提供上传、转换、生成 API；CLI 提供批量生成。

## 快速开始

### 环境准备

1) 建议使用虚拟环境：
```
python -m venv .venv
.\.venv\Scripts\activate
```
2) 安装依赖：
```
pip install -r requirements.txt
```

### 运行 Web
```
python src/web_interface/app.py
```
- 本机访问：`http://127.0.0.1:5000/`
- 局域网访问（如需）：将运行参数改为 `host="0.0.0.0"` 并在防火墙放行 5000 端口。

### 使用 CLI
```
python src/cli/generate_report.py --input examples/questions.txt --output examples/sorted_report.pdf --format pdf --sort-by-score
python src/cli/generate_report.py --input examples/questions.txt --output examples/sorted_report.docx --format docx --sort-by-score
```

## 接口说明（Web）
- `GET /` 首页，提供上传与生成表单
- `POST /upload` 上传文件（TXT/PDF/DOCX）
- `POST /convert` 仅进行格式转换（不评估）
- `POST /generate` 生成评估报告（默认按 `total_score` 降序）

## 输入格式建议
- 每道题以空行分隔，支持带 `题目：`/`答案：` 标识。
- 文本会进行中文分词与特征提取，评分包含多维度：计算复杂度、化学知识点、逻辑推理等。

## 常见问题
- 本机无法访问 `127.0.0.1:5000`：检查浏览器代理、防火墙是否拦截，或改用 `localhost:5000`。
- 中文显示：PDF 使用内置中文字体注册（如 `STSong-Light`），确保输出正常。
- 排序不生效：Web 端已改为 `generate_sorted_report`；CLI 可通过 `--sort-by-score` 开启（默认开启）。

## 目录结构（简化）
```
src/
  cli/generate_report.py        # CLI 入口
  output_generator/             # PDF/DOCX 生成器
  web_interface/app.py          # Flask Web 入口
chemistry-homework-classifier/  # 难度评估与PDF处理模块（内置）
```

## 发布到 GitHub
1) 初始化仓库并提交：
```
git init
git add -A
git commit -m "Initial commit: web + CLI with sorted reports"
```
2) 在 GitHub 创建远程仓库（例如 `yourname/chemistry-homework-classifier-web`）。
3) 关联远程并推送：
```
git branch -M main
git remote add origin https://github.com/yourname/chemistry-homework-classifier-web.git
git push -u origin main
```

> 如需将内置 `chemistry-homework-classifier` 独立管理为子模块，可后续改为 Git Submodule；当前版本直接内置源码，便于开箱即用。