#!/bin/bash
# 推送到GitHub脚本
# 使用方法: ./push_to_github.sh

echo "========================================"
echo "  推送到GitHub"
echo "========================================"
echo ""

# 检查是否在git仓库中
if [ ! -d .git ]; then
    echo "❌ 错误：当前目录不是git仓库"
    exit 1
fi

# 提示输入GitHub仓库URL
echo "请先在GitHub上创建新仓库，然后输入仓库URL"
echo "格式: https://github.com/你的用户名/仓库名.git"
echo ""
read -p "请输入GitHub仓库URL: " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ 错误：仓库URL不能为空"
    exit 1
fi

# 提示输入PAT
echo ""
echo "请输入GitHub Personal Access Token (PAT)"
echo "注意：输入时不会显示任何字符"
read -s pat

if [ -z "$pat" ]; then
    echo "❌ 错误：PAT不能为空"
    exit 1
fi

echo ""
echo "正在推送..."

# 构建带认证的URL
# 从 https://github.com/user/repo.git 提取 user/repo
repo_path=$(echo $repo_url | sed 's|https://github.com/||' | sed 's|.git$||')
auth_url="https://${pat}@github.com/${repo_path}.git"

# 添加远程仓库（如果不存在）
if ! git remote get-url origin &>/dev/null; then
    git remote add origin "$auth_url"
else
    git remote set-url origin "$auth_url"
fi

# 推送
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ 推送成功！"
    echo "========================================"
    echo ""
    echo "仓库地址: $repo_url"
    echo ""
    # 清除认证信息
    git remote set-url origin "$repo_url"
else
    echo ""
    echo "========================================"
    echo "❌ 推送失败"
    echo "========================================"
    echo ""
    echo "可能的原因："
    echo "  - PAT权限不足（需要repo权限）"
    echo "  - 仓库URL错误"
    echo "  - 网络连接问题"
fi
