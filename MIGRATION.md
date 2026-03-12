# 迁移指南 - 收并购分析套件

> 本文档说明如何将本套件迁移到不同的AI模型和设备

---

## 目录

1. [打包导出](#1-打包导出)
2. [迁移到 Claude Code](#2-迁移到-claude-code)
3. [迁移到 Kimi Code](#3-迁移到-kimi-code)
4. [迁移到 OpenClaw](#4-迁移到-openclaw)
5. [迁移到云端服务器](#5-迁移到云端服务器)
6. [迁移到其他AI工具](#6-迁移到其他ai工具)

---

## 1. 打包导出

### 方法1: 压缩包

```bash
# 在当前机器上
cd ~
zip -r ma-analysis-kit-export.zip ma-analysis-kit/

# 复制到目标设备
scp ma-analysis-kit-export.zip user@target-device:/path/

# 在目标设备上解压
unzip ma-analysis-kit-export.zip
```

### 方法2: Git 仓库

```bash
# 初始化Git仓库
cd ~/ma-analysis-kit
git init
git add .
git commit -m "Initial commit"

# 推送到远程 (GitHub/GitLab等)
git remote add origin https://github.com/yourusername/ma-analysis-kit.git
git push -u origin master

# 在目标设备上克隆
git clone https://github.com/yourusername/ma-analysis-kit.git
```

### 方法3: 云存储

```bash
# 压缩并上传到云存储
zip -r ma-analysis-kit.zip ma-analysis-kit/
# 上传到 iCloud / Dropbox / OneDrive / Google Drive

# 在目标设备上下载解压
```

---

## 2. 迁移到 Claude Code

### 步骤1: 复制文件

```bash
# macOS/Linux
cp -r ~/ma-analysis-kit/skills/ma-analysis ~/.claude/skills/

# 或者直接复制整个套件
cp -r ~/ma-analysis-kit ~/.claude/ma-analysis-kit
```

### 步骤2: 配置 MCP

```bash
# 添加金融数据 MCP
claude mcp add --transport http daloopa https://mcp.daloopa.com/server/mcp
claude mcp add --transport http factset https://mcp.factset.com/mcp

# 查看已配置的 MCP
claude mcp list
```

### 步骤3: 设置环境变量

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
export DALOOPA_TOKEN="your_token_here"
export TIANYANCHA_API_KEY="your_key_here"

# 重新加载配置
source ~/.zshrc
```

### 步骤4: 验证安装

```bash
# 启动 Claude Code
claude

# 在 Claude Code 中使用
> @ma-analysis init
> @ma-analysis collect --company "测试公司"
```

### 已知问题

| 问题 | 解决方案 |
|------|---------|
| MCP 连接失败 | 检查网络连接和 API Key |
| Skill 未找到 | 确认文件复制到正确的 `~/.claude/skills/` 目录 |
| 权限不足 | 使用 `chmod +x` 赋予脚本执行权限 |

---

## 3. 迁移到 Kimi Code

### 步骤1: 复制文件

```bash
# macOS/Linux
cp -r ~/ma-analysis-kit/skills/ma-analysis ~/.kimi/skills/

# Windows
xcopy /E /I %USERPROFILE%\ma-analysis-kit\skills\ma-analysis %USERPROFILE%\.kimi\skills\ma-analysis
```

### 步骤2: 配置 Kimi

编辑 `~/.kimi/config.toml`:

```toml
[skills]
ma-analysis = "~/.kimi/skills/ma-analysis"

[env]
DALOOPA_TOKEN = "your_token_here"
TIANYANCHA_API_KEY = "your_key_here"
```

### 步骤3: 验证安装

```bash
# 启动 Kimi Code
kimi

# 使用 Skill
> @ma-analysis 分析目标公司
```

---

## 4. 迁移到 OpenClaw

### 步骤1: 复制文件

```bash
cp -r ~/ma-analysis-kit/skills/ma-analysis ~/.openclaw/skills/
```

### 步骤2: 配置 OpenClaw

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "ma-analysis": {
      "path": "~/.openclaw/skills/ma-analysis",
      "enabled": true
    }
  },
  "mcp": {
    "daloopa": {
      "url": "https://mcp.daloopa.com/server/mcp"
    }
  }
}
```

### 步骤3: 重启 OpenClaw

```bash
# 杀死现有进程
pkill -f openclaw

# 重新启动
openclaw
```

---

## 5. 迁移到云端服务器

### 场景1: 阿里云/腾讯云/AWS 服务器

```bash
# 1. 本地打包
tar -czvf ma-analysis-kit.tar.gz ma-analysis-kit/

# 2. 上传到服务器
scp ma-analysis-kit.tar.gz root@your-server-ip:/root/

# 3. SSH登录服务器
ssh root@your-server-ip

# 4. 解压
tar -xzvf ma-analysis-kit.tar.gz

# 5. 安装依赖
cd ma-analysis-kit
pip install -r scripts/requirements.txt

# 6. 运行
python scripts/data_collector.py --help
```

### 场景2: Docker 容器

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY scripts/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scripts/data_collector.py"]
```

```bash
# 构建镜像
docker build -t ma-analysis-kit .

# 运行容器
docker run -v $(pwd)/data:/app/data ma-analysis-kit \
  python scripts/data_collector.py --company "目标公司"
```

---

## 6. 迁移到其他AI工具

### 通用方法

对于支持 Function Calling 或 MCP 的AI工具:

1. **复制 Skill 文件**
   ```bash
   cp -r ma-analysis-kit/skills/ma-analysis [目标目录]
   ```

2. **适配配置文件**
   - 根据目标工具的格式修改配置
   - 保留 `SKILL.md` 中的核心提示词

3. **测试验证**
   - 运行基本命令
   - 验证工具调用是否正常

### 适配清单

迁移到新工具时需要检查:

- [ ] 工具/函数定义格式
- [ ] 环境变量读取方式
- [ ] 文件系统访问权限
- [ ] 网络访问权限
- [ ] MCP 协议支持情况

### 手动使用 (无AI工具)

即使没有AI工具，也可以使用本套件:

```bash
# 1. 手动收集数据
python scripts/data_collector.py \
  --company "目标公司" \
  --output ./data

# 2. 手动填写模板
cp templates/report-template.md report.md
# 用文本编辑器手动填写 {{变量}}

# 3. 生成报告
python scripts/report_generator.py \
  --input ./data \
  --template templates/report-template.md \
  --output ./report \
  --company "目标公司"
```

---

## 数据迁移

### 导出历史数据

```bash
# 打包所有项目数据
tar -czvf ma-projects-backup.tar.gz ma-analysis-kit/projects/

# 导出数据库 (如有)
mysqldump -u user -p ma_database > ma_database_backup.sql
```

### 导入到新环境

```bash
# 解压数据
tar -xzvf ma-projects-backup.tar.gz -C ~/ma-analysis-kit/

# 导入数据库
mysql -u user -p ma_database < ma_database_backup.sql
```

---

## 验证清单

迁移完成后，运行以下验证:

```bash
# 1. 检查文件完整性
ls -la ~/ma-analysis-kit/
ls -la ~/ma-analysis-kit/skills/ma-analysis/

# 2. 检查依赖
pip list | grep -E "pandas|matplotlib|requests"

# 3. 运行测试
python scripts/data_collector.py --help
python scripts/report_generator.py --help

# 4. 测试AI工具集成
# 在AI工具中运行: @ma-analysis init
```

---

## 故障排除

### 问题1: 找不到 Skill

**症状**: AI 工具提示找不到 `@ma-analysis`

**解决**:
- 检查 Skill 文件路径是否正确
- 确认 `SKILL.md` 文件存在且格式正确
- 重启 AI 工具

### 问题2: MCP 连接失败

**症状**: 无法获取金融数据

**解决**:
- 检查网络连接
- 验证 API Key 是否有效
- 检查 MCP 服务器状态

### 问题3: 编码问题

**症状**: 中文显示乱码

**解决**:
```bash
# 设置 UTF-8 编码
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

### 问题4: 权限问题

**症状**: Permission denied

**解决**:
```bash
chmod +x QUICKSTART.sh
chmod +x scripts/*.py
```

---

## 获取帮助

- 查看 README.md 获取使用指南
- 查看 WORKFLOW.md 了解详细流程
- 提交 Issue 到项目仓库

---

**祝使用愉快!**
