
# 🌌 StarLink Pro : AI-Powered GoTo Telescope Control System

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python)
![Flet UI](https://img.shields.io/badge/UI-Flet_1.0_Beta-purple.svg?style=for-the-badge&logo=flutter)
![Platform](https://img.shields.io/badge/Platform-Win_|_Mac_|_Android-lightgrey.svg?style=for-the-badge)
![Hardware](https://img.shields.io/badge/Hardware-ESP32_Ready-orange.svg?style=for-the-badge&logo=espressif)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

**基于多线程异步架构与人工智能星空盲解的跨平台天文追踪中控系统**

</div>

---

## 📖 项目概述 (Overview)

**StarLink Pro** 是一款专为天文爱好者与极客打造的跨平台赤道仪/经纬仪中控软件。
本项目脱离了传统的臃肿星图软件，将**高精度开普勒轨道解析算法**与 **Astrometry.net 人工智能星野解析** 深度融合。配合底层的 UDP 高速无状态通信协议，可实现手机/PC端对下位机（如 ESP32、Arduino 步进电机驱动板）的毫秒级指向控制。

### ⚙️ 系统架构 (Architecture)
```text
[ 智能终端 (Flet UI) ]
   ├─ 自动 GPS/NTP 同步 (ipapi)
   ├─ 天文坐标解算引擎 (Math/Kepler)
   │
   ├─ [ 网络通信模块 ] ───── (Internet) ─────> [ Astrometry.net Cloud ]
   │                                              (AI 盲解星图特征匹配)
   │
   └─ [ UDP 广播协议 ] ───── (WLAN/LAN) ─────> [ ESP32 硬件驱动层 ]
                                                  (解析 RA/Dec 指令并驱动电机)

```

---

## ✨ 核心特性 (Key Features)

### 1. 🧮 纯数学原生天文解算引擎

* 不依赖庞大的天文星表库，底层手搓**儒略日(Julian Date)推演**与**开普勒轨道根数**计算。
* 实时解算太阳 (Sun)、月球 (Moon) 与火星 (Mars) 的赤道坐标 (RA/Dec)。
* 结合自动获取的观测者经纬度，动态进行**球面三角学坐标系转换**，输出用于物理电机的地平坐标 (Alt/Az)。

### 2. 🤖 异步 AI 星野解算 (Plate Solving)

* 接入权威的 Astrometry 星图特征数据库。
* 采用 `asyncio` 与多线程混合并发架构，在后台无感完成图片上传、Job 轮询、数据回传，**主 UI 线程达到 0 卡顿**。
* 支持 Android 端字节流 (`bytes`) 与桌面端绝对路径 (`path`) 的多态文件读取。

### 3. 📡 极简极速的下位机握手协议

* 专为单片机优化的轻量级 UDP 通信，抛弃繁重的 TCP 握手。
* 固定的指令负荷，极低延迟，完美适配自制星野赤道仪或 GoTo 经纬仪底座。

---

## 📂 项目结构 (Project Structure)

```text
StarLink-Pro/
├── assets/                 # UI 静态资源与图标
├── main.py                 # 核心应用逻辑、UI 渲染与算法引擎
├── .env                    # (需手动创建) 存放私密环境变量
├── .gitignore              # Git 忽略配置
└── requirements.txt        # Python 依赖清单

```

---

## 🛠️ 部署与安装 (Installation)

推荐使用 Python 虚拟环境（Virtual Environment）来运行此项目，避免污染全局环境。

**1. 克隆仓库**

```bash
git clone [https://github.com/你的用户名/StarLink-Pro.git](https://github.com/你的用户名/StarLink-Pro.git)
cd StarLink-Pro

```

**2. 创建并激活虚拟环境**

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

```

**3. 安装核心依赖**

```bash
pip install -r requirements.txt

```

**4. 秘钥配置 (Environment Variables)**
在项目根目录新建一个 `.env` 文件，并填入你从 [Astrometry Nova](https://nova.astrometry.net/) 获取的 API Key：

```env
ASTROMETRY_API_KEY=your_real_api_key_here

```

---

## 🕹️ 硬件通信协议 (Hardware Protocol)

若您打算自行开发接收端硬件（如 ESP32），请配置您的单片机监听本地端口 `8888` 的 UDP 协议。

**StarLink Pro 发送的 Payload 格式：**

```text
<RA_FLOAT>,<DEC_FLOAT>

```

* **示例**：`253.1415, -45.6789`
* **说明**：赤经 (RA) 和赤纬 (Dec) 均保留 4 位小数，以英文逗号分隔，采用 UTF-8 编码发送。下位机收到字符串后进行 `split(',')` 即可驱动电机解析。

---

## 📱 打包为独立 App (Build for Android)

得益于 Flet 的强力跨平台特性，您可以一键将本项目编译为 Android APK：

1. 确保您的开发机已配置好 **Flutter SDK** 与 **Android Studio 工具链**。
2. 在终端执行打包指令：

```bash
flet build apk --project-name "StarLinkPro" --org "com.geek.starlink"

```

3. 编译完成后，前往 `build/apk/` 目录下获取您的专属 `app-release.apk` 安装包。

---

## 📄 开源协议 (License)

本项目基于 [MIT License](https://www.google.com/search?q=LICENSE) 协议开源。欢迎硬件创客与天文同好 Fork、提交 PR 并将它应用到你的 DIY 天文望远镜项目中！

```

***




```
