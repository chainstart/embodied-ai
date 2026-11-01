# 用通用大模型控制具身机器人：2026 年 9 月以来进展与入门硬件建议

整理日期：2026-11-01。文中数字多为各团队自报，未经独立复现。

## 1. 发生了什么

2026 年 9 月初，OpenAI 的 GPT-6 Astra 被大量开发者直接用来控制机械臂，且**不做任何机器人专用训练**。一台约 150 美元的 SO-101 机械臂画出金门大桥的视频被大量转发，之后两个月出现了 40 多个案例、十几个评测基准和一批 arXiv 论文。
社区汇总列表：`repos/Awesome-Astra-Embodied-AI`。

主流做法可以概括为下面四种，按落地难度从低到高排列：

| 范式 | 大模型的职责 | 代表工作 |
|---|---|---|
| A. 技能选择 | 读取结构化场景，从预定义技能（抓、放、推）里选一个 | AgileX `piper-astra-jev`（Grounding DINO + SAM 3 感知，MuJoCo IK，CAN 控制） |
| B. 直接输出末端位姿 | 每步看多路相机图像，调用 `move_to(x,y,z,rpy,gripper)`，由 IK 换算成关节角 | RoboCurve / Inspect Robots、AA-Robotics |
| C. 编程智能体当策略（Agent as Policy） | 在 Codex CLI 等环境里自己写脚本、看图、三角测量、改代码 | AGP (arXiv 2609.12541)：YAM 真机 8 种配置中 7 种成功率 ≥80% |
| D. 大模型 + VLA 分层 | 大模型负责规划、纠错和记忆，冻结的 VLA（π0.5 等）负责底层动作 | Spotter (2609.36808)：π0.5 成功率从 53% 提到 83%；RPent / Harness-VLA；RoboICL |

另一条线是让大模型去**写仿真环境、做 Real2Sim 重建、搭 RL 训练流程**（Isaac Lab 转笔、MuJoCo 重建、PPO 调参），即把大模型当"机器人研究员"用。

## 2. 关键评测结论

| 评测 | 结果 |
|---|---|
| RoboCurve（YAM 双臂，`move_to`） | 积木放入碗：Astra 19/20，Fable 5.1 8/20；拼图嵌入槽：两者都是 2/20 |
| AA-Robotics v0.1（幻尔 NexArm 真机，8 个桌面任务） | Astra 69.4 > GPT-6.1 Sol 64.6 > Gemini 4 Argon 55.3 > Opus 5.5 48.8 > Fable 5.1 46.3；每个任务约 30 分钟，比人慢约 100 倍；Astra 每任务约 $16 |
| RoboDojo（42 个仿真任务） | 裸用 Astra 成功率 22.5%（同类模型 GPT-5.5 仅 0.9%）；配上 AGP 编程智能体框架后为 56% |
| 2610.28259 系统评测 | RoboTwin 2.0 76%；几何约束任务（LIBERO-GeoMotion）零样本仅 11% |
| SafeHarness (2609.20822) | 不加约束层时，智能体常常完成任务却撞上障碍物；加障碍感知层后碰撞避免率达 91.9% |
| 触觉 (2610.28457) | 把触觉读数交给模型后，插孔任务成功率从 31% 提到 99% |

**结论**：语义理解和泛化能力很强，开箱即可完成简单抓放；但在精度、速度、成本、安全性和对任务是否完成的判断上仍有明显短板。RoboDojo 团队就因安全原因中止了真机实验，网上也有 Astra 指挥机械臂混合漂白剂和氨水的演示。**工程框架（harness）的设计比模型本身更决定成败**，这也是个人研究最容易出成果的方向。

## 3. 硬件建议（以京东为渠道）

京东页面无法抓取实时价格，下面的价格均为公开报道或海外标价的估算，**下单前请以商品页为准**。标注"自营"的是京东搜索页显示带自营标签的 SKU。

### 方案一：入门（约 1–3 千元）：SO-101 / SO-ARM101（推荐首选）
- 理由：LeRobot 官方支持；`inspect-robots` 已有 `so_arm` 插件（`repos/inspect-robots`）；爆火的金门大桥演示用的就是它。
- 京东有瓴乐、ROKID、幻尔、矽递等多家第三方店铺销售，**目前没看到自营**。建议买"成品到手即用 + 双摄像头（手眼 + 固定）"版本，例如 ROKID 双相机套件 `item.jd.com/10236557839126.html`。
- 局限：舵机精度和负载都低，只适合轻物体抓放和画画。

### 方案二：复现 AA-Robotics 基准：幻尔 NexArm（约 2.8–6 千元）
- AA-Robotics 榜单用的就是这款臂，可以直接和榜单结果对比。支持 USB 串口、WiFi，兼容 LeRobot。
- 京东为幻尔第三方店铺，例如标准版 `item.jd.com/10215871981548.html`。

### 方案三：科研级（约 1.5 万元起）：松灵 PiPER（有自营）
- CAN 接口 + Python SDK，支持 ROS1/2，有现成的 Astra 开源工程 `repos/piper-astra-jev`。负载 1.5kg，重复定位精度高。
- 自营 SKU：PiPER `item.jd.com/100282474671.html`，H 系列 `100374993676`，L 系列 `100374991546`。2024 年发布价为单臂 14999 元（不含夹爪）。
- 备选：矽递 reBot Arm B601-RS（自营 `100303836421`；含 D405 深度相机的套装 `100395124458`）。它是 6+1 自由度的 QDD 电机，走 USB-CAN，支持 LeRobot 和 Isaac Sim；许可为 CC BY-NC-SA，商用前需确认。

### 配套设备
- **深度相机**：Intel RealSense D405 / D435i，或奥比中光 Gemini 系列。piper-astra-jev 用的是 RealSense。
- **电脑**：只调用云端 API 时普通笔记本即可；要在本地跑 Grounding DINO、SAM 3 或 VLA，需要 RTX 4090 级别的显卡。
- **急停按钮**、桌面夹具、软质积木和泡沫块等测试道具。
- **API 预算**：每个任务约 $1–16。

### 进阶：移动本体
- 宇树 Go2 已接入京东自营，Pro 版约 1.6–2 万元。适合做"大模型规划 + 底层运控"的实验，但不适合入门。

## 4. 建议的实验路线

1. **零硬件起步**：`inspect-robots` 自带 mock 和 CubePick 环境，先把"大模型 → 工具调用 → 观测"的闭环跑通。
2. **SO-101 真机**：复现积木放碗任务，比较范式 A 和范式 B 两种接口，记录成功率、耗时和费用。
3. **加约束层**：工作空间边界、限速、碰撞检查，参考 SafeHarness。
4. **加记忆和经验复用**：参考 AGP 的经验文件和 RoboICL。
5. **升级到 PiPER 或 reBot**：跑 piper-astra-jev，尝试大模型 + VLA 分层（参考 Spotter）。

## 5. 本目录内容

> 论文 PDF 和第三方仓库不随本仓库分发，运行 `scripts/fetch_refs.sh` 可重新下载。

- `papers/`：8 篇 arXiv 论文 PDF
  - 2609.12541 AGP（Agent as Policy）
  - 2609.24170 RoboDojo 评测
  - 2609.20822 SafeHarness
  - 2610.28259 直接控制系统评测
  - 2609.34261 RoboICL
  - 2609.36808 Spotter
  - 2610.28457 触觉
  - 2609.33378 RHD
- `repos/Awesome-Astra-Embodied-AI`：案例与评测汇总
- `repos/agent-as-policy`：AGP 代码，含硬件桥和 RoboDojo 评测
- `repos/piper-astra-jev`：PiPER + Astra 的完整工程
- `repos/inspect-robots`：大模型机器人评测框架，支持 SO-101、YAM 和 mock 环境

## 来源
- https://github.com/zjwzcx/Awesome-Astra-Embodied-AI
- https://openai.robocurve.org/gpt-6-astra/
- https://artificialanalysis.ai/articles/aa-robotics
- https://agent-as-policy-2026.github.io/
- https://global.agilex.ai/blogs/robotics/how-to-control-robotic-arm-with-gpt-6-astra-and-jev-llm-model
- https://arxiv.org/abs/2609.24170 · https://arxiv.org/abs/2609.20822 · https://arxiv.org/abs/2610.28259
- https://www.jd.com/hprm/670cb5cdb6bc1873ec0.html（京东开源机械臂频道）
- https://wiki.seeedstudio.com/rebot_arm_b601_rs_lerobot/
- https://news.qq.com/rain/a/20260101A01M0600（宇树接入京东自营）
- https://rcdrone.top/zh/products/nexarm · https://news.qq.com/rain/a/20240821A01KTP00（PiPER 定价）

## 6. 仿真原型（2026-11-01 新增）
- `sim/`：SO-101 + GPT-6 Astra 的 MuJoCo 仿真实验平台。工具 API、安全层、自动评分和日志都齐了，仿真和真机共用一套接口。用法见 `sim/README.md`。
