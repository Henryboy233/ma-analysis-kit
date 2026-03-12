# 收并购分析套件 - 文件清单

## 核心文档

| 文件 | 说明 | 必需 |
|------|------|------|
| `README.md` | 主文档，使用指南 | ✓ |
| `WORKFLOW.md` | 标准工作流程文档 | ✓ |
| `MIGRATION.md` | 迁移指南 | ✓ |
| `QUICKSTART.sh` | 快速开始脚本 | ✓ |
| `verify.sh` | 环境验证脚本 | ✓ |
| `export.sh` | 导出打包脚本 | ✓ |
| `MANIFEST.md` | 本文件 | |

## 技能定义

| 文件 | 说明 | 必需 |
|------|------|------|
| `skills/ma-analysis/SKILL.md` | AI Skill 定义文件 | ✓ |

## 模板

| 文件 | 说明 | 必需 |
|------|------|------|
| `templates/report-template.md` | 分析报告模板 | ✓ |

## 检查清单

| 文件 | 说明 | 必需 |
|------|------|------|
| `checklists/data-collection.md` | 数据收集检查清单 | ✓ |

## API 模块

| 文件 | 说明 | 必需 |
|------|------|------|
| `apis/__init__.py` | API模块导出 | ✓ |
| `apis/tianyancha_api.py` | 天眼查API封装 | ✓ |
| `apis/tushare_api.py` | Tushare API封装 | ✓ |
| `apis/api_manager.py` | API统一管理器 | ✓ |
| `apis/README.md` | API模块说明 | |

## 配置

| 文件 | 说明 | 必需 |
|------|------|------|
| `config/api_config.example.py` | API配置示例 | ✓ |

## 脚本

| 文件 | 说明 | 必需 |
|------|------|------|
| `scripts/data_collector.py` | 数据采集脚本 | ✓ |
| `scripts/report_generator.py` | 报告生成脚本 | ✓ |
| `scripts/requirements.txt` | Python依赖列表 | ✓ |

## 示例

| 文件 | 说明 | 必需 |
|------|------|------|
| `examples/api_usage_demo.py` | API使用示例 | ✓ |

## 总文件数

- Markdown 文档: 7
- Python 脚本: 6
- Shell 脚本: 3
- 配置文件: 1
- **总计: 17 个文件**

## 目录结构

```
ma-analysis-kit/
├── README.md                 # 主文档
├── WORKFLOW.md              # 工作流程
├── MIGRATION.md             # 迁移指南
├── MANIFEST.md              # 文件清单
├── QUICKSTART.sh            # 快速开始
├── verify.sh                # 验证脚本
├── export.sh                # 导出脚本
├── .gitignore               # Git忽略
├── skills/
│   └── ma-analysis/
│       └── SKILL.md         # AI Skill
├── templates/
│   └── report-template.md   # 报告模板
├── checklists/
│   └── data-collection.md   # 检查清单
├── apis/                    # API模块
│   ├── __init__.py
│   ├── tianyancha_api.py
│   ├── tushare_api.py
│   ├── api_manager.py
│   └── README.md
├── config/
│   └── api_config.example.py
├── scripts/
│   ├── data_collector.py
│   ├── report_generator.py
│   └── requirements.txt
└── examples/
    └── api_usage_demo.py
```

## 文件大小统计

```bash
# 查看各目录大小
du -sh ~/ma-analysis-kit/*

# 查看总大小
du -sh ~/ma-analysis-kit/
```

## 完整性校验

运行以下命令验证套件完整性:

```bash
cd ~/ma-analysis-kit
./verify.sh
```

## 快速导出

```bash
# 打包整个套件
./export.sh

# 输出位置: exports/ma-analysis-kit-v{version}-{timestamp}.tar.gz
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-12 | 初始版本，含核心流程和模板 |
| 1.1.0 | 2026-03-12 | 新增API模块（天眼查+Tushare） |

---

**注意**: 本套件不含任何商业数据或敏感信息，可自由复制和迁移。
