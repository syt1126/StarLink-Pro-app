# 🌌 StarLink Pro 

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flet Version](https://img.shields.io/badge/UI-Flet-purple)
![License](https://img.shields.io/badge/License-MIT-green)

**StarLink Pro** 是一款基于 Python 和 Flet 框架开发的跨平台智能天文解算与追踪控制软件。它结合了实时天文算法与人工智能星野解析（Plate Solving），能够精准计算天体坐标，并通过 UDP 协议将追踪指令发送给下位机（如 ESP32 步进电机控制板），实现自动寻星与追踪。

---

## ✨ 核心功能 (Features)

- **📍 自动地理定位与授时**：启动时自动通过网络获取观测者的经纬度，并同步当前系统时间，无需繁琐的手动校准。
- **🪐 实时天体坐标解算**：内置高精度开普勒轨道算法，实时计算太阳 (Sun)、月亮 (Moon) 和火星 (Mars) 的赤经/赤纬 (RA/Dec) 以及高度角/方位角 (Alt/Az)。
- **🤖 AI 盲解星图 (Plate Solving)**：集成全球权威的 [Astrometry.net](https://nova.astrometry.net/) API。一键上传星空照片，AI 自动识别星区并返回精准坐标，支持多线程异步无感解析。
- **📡 局域网 UDP 通信**：极简配置 ESP32 IP 地址，一键将目标坐标发送至下位机，实现从软件到硬件的无缝对接。
- **📱 响应式暗黑 UI**：专为夜间观测设计的深色模式界面，保护暗视觉，支持跨平台（Windows/macOS/Android/iOS）运行。

---

## 🛠️ 安装指南 (Installation)

1. **克隆仓库到本地**
   ```bash
   git clone [https://github.com/你的用户名/StarLink-Pro.git](https://github.com/你的用户名/StarLink-Pro.git)
   cd StarLink-Pro

```

2. **安装依赖库**
确保你的电脑已安装 Python 3.8+ 环境，然后运行：
```bash
pip install -r requirements.txt

```


3. **配置 API 密钥 (重要！)**
本项目使用 Astrometry.net 进行星图识别。你需要前往 [Astrometry.net](https://nova.astrometry.net/) 注册并获取你自己的 `API KEY`。
> **注意**：请勿在公开代码中暴露你的 API Key，建议使用 `.env` 环境变量文件进行配置加载。



---

## 🚀 快速开始 (Usage)

在项目根目录下直接运行：

```bash
python main.py

```

*(如果是桌面端，也可以使用 Flet 命令：`flet run main.py`)*

### 操作步骤：

1. **连接硬件**：在页面上方输入你的 ESP32 接收端 IP 地址（默认 `192.168.68.107`）。
2. **快捷追踪**：点击 `Sun`、`Moon` 或 `Mars`，系统会瞬间解算当前位置下的天体坐标，并在下方显示。
3. **AI 识图**：点击 `Select Photo / 自动识别`，选择一张星空照片，等待几秒钟解析完成后，坐标会自动填入输入框。
4. **发送指令**：确认坐标无误后，点击底部的 `Send to Motors / 手动发送`，指令将通过 UDP 广播至硬件端。

---

## 📦 编译为手机 App (APK 打包)

如果你希望将此代码打包为 Android 手机上独立运行的 App，请确保已配置好 Flutter 及 Android Studio 环境，然后运行：

```bash
flet build apk --project-name "StarLinkPro" --org "com.yourname.starlink"

```

编译成功后，在 `build/apk/` 目录下即可找到 `app-release.apk` 文件。

---

## 🙏 致谢 (Acknowledgments)

* UI 框架：[Flet](https://flet.dev/)
* 盲解引擎：[Astrometry.net API](https://nova.astrometry.net/api_help)

```

---





```
