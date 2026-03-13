#!/usr/bin/env python3
"""
启动Agent管理平台
"""

import subprocess
import sys
import os

# 设置环境变量
os.environ["AGENT_MODE"] = "1"

# 启动Agent平台
subprocess.run([
    sys.executable, "-m", "streamlit", "run", "agent_platform.py",
    "--server.port=8502",
    "--server.headless=true"
])
