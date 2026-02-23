

```markdown
# 🌌 StarLink Pro: 跨平台智能星野追踪控制终端

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python)
![Flet UI](https://img.shields.io/badge/UI-Flet_1.0_Beta-purple.svg?style=for-the-badge&logo=flutter)
![Astrometry](https://img.shields.io/badge/API-Astrometry.net-005571.svg?style=for-the-badge&logo=api)
![Asyncio](https://img.shields.io/badge/Concurrency-Asyncio_%7C_Threading-red.svg?style=for-the-badge)
![Hardware](https://img.shields.io/badge/Hardware-ESP32_Ready-orange.svg?style=for-the-badge&logo=espressif)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

**融合开普勒轨道解析、异步 AI 盲解与微秒级 UDP 遥测的天文控制系统**

</div>

---

## 📖 项目摘要 (Abstract)

**StarLink Pro** 是一套去中心化的轻量级天文设备中控台。区别于传统 Stellarium/ASCOM 笨重的生态，本项目专为**极客自制赤道仪/经纬仪**设计。
系统不仅内置了纯数学推演的天体历表算法，还创新性地引入了 **AI Plate Solving（星图盲解）** 技术。通过 Flet 框架实现跨平台（Windows/macOS/Android/iOS）一致的暗视觉 UI 体验，并利用无状态 UDP 协议完成与底层电机驱动板的极速握手。

---

## 🧠 核心架构深潜 (Deep Dive)

### 1. 天文推演引擎 (Astrodynamics Engine)
脱离对庞大离线星表（如 Tycho/UCAC）的依赖，系统直接在内存中基于**儒略日 (Julian Date)** 与**开普勒轨道根数 (Keplerian Elements)** 进行实时浮点运算：
* **时间与坐标基准**：后台守护线程 (`daemon=True`) 通过 `ipapi.co` 自动校准观测者经纬度 (Lat/Lon)，并同步 UTC 时间。
* **黄道到赤道转换**：通过黄赤交角 ($\epsilon \approx 23.44^\circ$) 公式，精准计算日月火星的赤经 (RA) 与赤纬 (Dec)。
* **赤道到地平转换 (球面三角学)**：
  系统实时计算格林尼治平恒星时 (GMST) 与地方恒星时 (LST)，推导出目标天体的时角 (HA)，进而计算出适配物理电机的**高度角 (Alt) 与方位角 (Az)**。

### 2. AI 盲解状态机 (Astrometry Plate Solving)
针对无 GoTo 对齐的设备，系统集成了 Astrometry.net 的云端解析能力。为了保证 UI 绝对流畅，底层实现了复杂的**多线程异步状态机**：
1. **Session Handshake**: 验证 `.env` 中的 API Key，获取有效期 Session。
2. **Payload Upload**: 兼容桌面端路径 (`filepath`) 与移动端内存流 (`bytes`)，以 `degwidth` 模式（0.1~180度）动态上传星区特征。
3. **Async Polling**: 在 `asyncio.run_in_executor` 线程池中执行长达 90 秒的阻塞轮询，分为 `Sub_ID` 队列等待与 `Job_ID` 计算解析双重阶段，并通过主线程 `page.update()` 实时映射进度。

### 3. Flet 响应式事件循环 (Event Loop)
* **并发隔离**：时钟刷新 (`update_clock`)、网络定位 (`update_location_from_network`) 使用独立 Thread 运行；AI 识别与 UI 交互使用 AsyncIO 协程。
* **暗视觉保护 (Dark Vision)**：全局 `#111111` 与深色高对比度（Cyan/Purple）卡片设计，严防夜外场观测时屏幕强光破坏人眼暗适应。

---

## 🔌 硬件遥测协议 (Hardware Telemetry Specs)

系统通过标准的 `socket.SOCK_DGRAM` 协议向局域网内的单片机（ESP32 / Arduino / 树莓派）发送控制流。

* **通信端口**: `UDP 8888`
* **超时机制**: `1.5s` (防止线程阻塞)
* **数据包载荷 (Payload)**: `UTF-8` 编码的字符串
* **格式定义**: `RA,DEC` (浮点数，保留 4 位小数)
  
**下位机 (C++ / Arduino) 接收伪代码示例**：
```cpp
// 当 ESP32 收到 UDP 包时
String payload = udp.readString(); // 例: "185.1234,45.6789"
int commaIndex = payload.indexOf(',');
float target_ra = payload.substring(0, commaIndex).toFloat();
float target_dec = payload.substring(commaIndex + 1).toFloat();
// 将 target_ra 和 target_dec 转换为步进电机脉冲 ...

```

---

## 🚀 部署与运行 (Deployment)

### 环境依赖清单 (requirements.txt)

请确保你的项目中存在 `requirements.txt` 并包含以下内容：

```text
flet>=0.80.0
requests>=2.31.0
python-dotenv>=1.0.0

```

### 1. 本地测试运行

```bash
# 1. 克隆代码
git clone [https://github.com/你的用户名/StarLink-Pro.git](https://github.com/你的用户名/StarLink-Pro.git)
cd StarLink-Pro

# 2. 配置环境
python -m venv venv
source venv/bin/activate  # Windows 用户使用: .\venv\Scripts\activate
pip install -r requirements.txt

# 3. 注入安全密钥
echo "ASTROMETRY_API_KEY=你的真实API_KEY" > .env

# 4. 点火启动
python main.py

```

### 2. 跨平台编译 (Build to Standalone)

使用 Flet CLI 将 Python 源码直接转化为原生应用程序：

```bash
# 编译为 Windows / macOS 桌面可执行文件
flet build windows  # 或 macos

# 编译为 Android APK (需预装 Flutter SDK)
flet build apk --project-name "StarLinkPro" --org "com.astronomy.starlink"

```

---

## 🗺️ 演进路线图 (Roadmap)

* [x] 开普勒轨道算法引擎与 LST 恒星时同步
* [x] Astrometry API 接入与异步无感解析
* [x] ESP32 UDP 伺服控制协议
* [ ] 接入 ASCOM / INDI 工业标准驱动
* [ ] 增加梅西耶天体 (Messier Objects) 本地离线星表
* [ ] 离线 Plate Solving 支持 (ASTAP 引擎桥接)

---

## 🤝 贡献与许可 (Contributing & License)

本项目采用 [MIT License](https://www.google.com/search?q=LICENSE) 授权。欢迎任何形式的 Pull Requests。
如果您在 DIY 天文台/赤道仪的路上使用了本项目，欢迎在 Issue 中分享您的作品！


```
