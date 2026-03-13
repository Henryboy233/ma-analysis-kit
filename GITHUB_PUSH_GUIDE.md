# GitHub推送指南

## 方法：使用 Personal Access Token (PAT)

### 步骤1：在GitHub创建仓库
1. 访问 https://github.com/new
2. 输入仓库名：`ma-analysis-kit`
3. 选择「Public」或「Private」
4. **不要**初始化README（已有）
5. 点击「Create repository」

### 步骤2：使用脚本推送（推荐）

```bash
cd ~/ma-analysis-kit
chmod +x push_to_github.sh
./push_to_github.sh
```

按提示输入：
- 仓库URL（如 `https://github.com/yourusername/ma-analysis-kit.git`）
- PAT（已提供，复制粘贴即可）

### 步骤3：手动推送（备选）

如果脚本失败，手动执行：

```bash
cd ~/ma-analysis-kit

# 1. 设置远程仓库（替换yourusername）
git remote add origin https://github.com/yourusername/ma-analysis-kit.git

# 2. 使用PAT推送（交互式输入密码时粘贴PAT）
git branch -M main
git push -u origin main
```

推送时会提示输入密码，此时输入PAT即可。

### 步骤4：验证

推送成功后访问：
```
https://github.com/yourusername/ma-analysis-kit
```

应能看到所有项目文件。

---

## PAT权限说明

当前PAT具有 `repo` 权限，可以：
- ✅ 读取仓库
- ✅ 推送代码
- ✅ 创建仓库
- ❌ 删除仓库（需要额外权限）

## 安全提醒

1. **不要将PAT提交到代码中**
2. **定期轮换PAT**（GitHub建议90天）
3. **仅在此设备上使用PAT**
4. **推送完成后清除终端历史**（可选）

## 后续使用

推送完成后，以后更新代码只需：

```bash
git add .
git commit -m "更新说明"
git push
```

不再需要输入PAT（使用git credential缓存）。
