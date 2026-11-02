# SO-101 + GPT-6 Astra 仿真原型

在 MuJoCo 里用通用大模型（默认 `gpt-6-astra`）直接控制 SO-101 机械臂，自动评分、记录和统计。
架构是**仿真和真机可互换**：智能体、工具 API、安全层、日志都是共用的，只需替换最底层的后端。

```
GPT-6 Astra (OpenAI Responses API, function calling + 图像)
        │  move_to / move_relative / set_gripper / move_joints / go_home
        │  get_observation / pixel_to_world / finish
RobotTools  ── 安全层：工作空间边界、桌面下限、IK 可达性检查、限速
        │  （关节空间命令 + 相机图像 + 深度反投影）
SimBackend (MuJoCo)  ⇄  RealSO101Backend（预留接口，基于 LeRobot）
        └─ 旁路：评分器（读取仿真真值，0–4 阶段）+ EpisodeLogger
```

## 快速开始

```bash
cd /workspace/embodied-ai/sim
./setup.sh           # 首次：创建 .venv；无系统 OpenGL 时免 root 下载 OSMesa 到 .gl/
source env.sh        # 加载软件渲染（OSMesa）环境变量

# 1) 用"作弊"脚本验证管线（读仿真真值，无需 API key）
.venv/bin/python run_episode.py --agent oracle --seeds 0-4

# 2) 离线检查大模型循环（假 API 客户端）
.venv/bin/python run_episode.py --agent dry-run --seeds 0

# 3) 正式实验
export OPENAI_API_KEY=sk-...
# export OPENAI_BASE_URL=https://你的中转/v1   # 需要代理或中转时
.venv/bin/python run_episode.py --agent astra --seeds 0-9 --effort medium
```

## 查看仿真环境

有三种方式：

**1. 交互式 3D 窗口**（需要有显示器。Windows 11 的 WSLg 可以直接弹出 Linux 窗口）
```bash
# 在你自己的 WSL Ubuntu 终端里运行，不要在没有显示器的容器里运行
cd ~/work/projects/embodied-ai/sim
./setup.sh                 # 如果 .venv 是在别的机器或容器里建的，会自动重建
source env.sh              # 检测到 DISPLAY 时使用系统 OpenGL，会打印 MUJOCO_GL=default
.venv/bin/python view_scene.py --seed 0                                    # 只看场景，可以用鼠标拖动、旋转、施力
.venv/bin/python run_episode.py --agent oracle --seeds 0-2 --viewer        # 实时观看脚本完成任务
.venv/bin/python run_episode.py --agent astra --seeds 0 --viewer           # 实时观看大模型操作
```
- 鼠标操作：左键拖动旋转，右键拖动平移，滚轮缩放，双击选中物体，Ctrl+右键拖动对选中物体施力。右侧面板可以切换相机（front/top/side/wrist），也可以显示接触点。
- `--viewer-speed 2` 以 2 倍速播放；`--viewer-hold 10` 让每个回合结束后窗口多停留 10 秒。关掉窗口不影响实验，仿真会在后台继续跑完。
- 大模型思考期间机械臂处于静止状态。窗口会照常刷新，不会因为等待而快进。
- 如果窗口打不开，报错 `could not initialize GLFW`：先运行 `echo $DISPLAY` 确认 WSLg 可用（应该是 `:0`）。如果提示缺少库，运行 `sudo apt install libgl1 libegl1 libglfw3`。

**2. 看录像**：每次运行都会生成 `runs/<批次>/seedNNN/rollout.gif`（前视相机）。在 Windows 资源管理器里打开 `\\wsl.localhost\Ubuntu\home\biostar\work\projects\embodied-ai\sim\runs\` 即可。

**3. 看模型看到的画面**：`runs/<批次>/seedNNN/images/` 里是每一步回传给模型的相机图像，`transcript.md` 是图文对照的完整过程。

常用参数：

| 参数 | 说明 |
|---|---|
| `--model` | 默认 `gpt-6-astra`，可换成任何支持 Responses API 和 function calling 的模型 |
| `--effort low/medium/high` | 推理强度 |
| `--cameras front,top,wrist` | 每一步回传哪些相机图像（另有 `side`） |
| `--context server/window` | server 由服务端保留完整历史；window 只保留最近 `--image-window` 次观测的图像，省钱 |
| `--detail low/high` | 图像精度 |
| `--no-grid` | 关掉图像上的像素网格 |
| `--task cube_in_bowl/cube_in_bowl_hard` | hard 版本多一个干扰方块 |
| `--max-turns`、`--max-wall` | 预算上限 |
| `--price-*` | 计费单价。默认 $10 / $1 / $50 每百万 token，来自第三方页面，未核实 |

## 输出（`runs/<时间>_<任务>_<agent>/`）
- `batch_summary.json`：成功率、平均阶段、**谎报成功次数**、碰撞次数、平均费用和耗时
- `seedNNN/transcript.md`：可读的完整对话与动作记录（每步附评分阶段）
- `seedNNN/episode.jsonl`：结构化事件（工具调用、结果、token 用量、评分）
- `seedNNN/images/`：每步回传给模型的图像
- `seedNNN/rollout.gif`：前视相机录像（`--no-gif` 可关闭，能明显提速）

## 已验证
- oracle 脚本（读仿真真值）在 12 个随机布局（共 20 次运行）上全部成功，说明物理、IK、夹爪、评分器和日志都能工作。
- dry-run 在 server 和 window 两种上下文模式下都通过了请求格式检查。
- **尚未验证**：真实 `gpt-6-astra` API 调用。本机没有 API key，第一次运行请留意报错。

## 关键设计说明
- **机械臂模型**：TheRobotStudio/SO-ARM100 官方 MJCF（`so101_new_calib_camera.xml`）。在此基础上加了腕部相机、`grasp_center` 抓取中心点（距固定爪内侧 2.2cm）和两块平面摩擦垫。原始凸包网格接触点太少，转动手腕时方块会滑落。
- **5 自由度的限制**：竖直向下（pitch −90°）的可达范围很窄。被拒绝时，安全层会告诉模型这个点在哪些俯仰角下可达。这与真机一致，不是 bug。
- **只给模型真机也能拿到的信息**：RGB 图像、关节角、夹爪指令与实测开度（夹住东西时实测 > 指令）、深度反投影（真机对应 RealSense 加手眼标定）。物体真值只给评分器和 oracle。
- **安全层**：越界、低于桌面、IK 不可达的命令会被拒绝；机械臂碰到桌面会立刻停止；非夹爪部位撞到物体会发出警告。这些都计入统计。

## 迁移到真机
实现 `so101sim/backend.py` 里的 `RealSO101Backend`（注释中有 LeRobot `SO101Follower` 的对接要点）。
它需要提供 `joint_positions / move_joints / set_gripper / gripper_state / render / deproject`，上层代码不需要改。
关节零位和方向要先标定到与 MuJoCo 模型一致，这样同一套 IK 才能用在真机上。

## 可以做的实验
1. 不同推理强度、相机组合、图像精度对成功率和费用的影响
2. server 和 window 上下文的成本与性能对比（AA-Robotics 发现约 70% 的费用来自上下文）
3. 去掉像素网格或 `pixel_to_world`：模型自身的空间估计能力有多强
4. 修改 `prompts/system.md`：提示词工程或经验文件（参考 AGP）
5. 增加任务：堆叠、排序、带障碍物（参考 SafeHarness）
6. 对比其他模型（`--model`）

## 文件
```
sim/
  run_episode.py           命令行入口：批量运行、评分、汇总（--viewer 实时窗口）
  view_scene.py            在交互式 MuJoCo 窗口里查看场景
  prompts/system.md        系统提示词（{FRAME_DOC} 会被替换为坐标系说明）
  so101sim/scene.py        场景生成与随机布局（机械臂补丁、桌子、方块、碗、相机）
  so101sim/kinematics.py   5 自由度 DLS 逆运动学（位置 + 接近俯仰角 + 腕部翻滚）
  so101sim/backend.py      RobotBackend 接口、SimBackend、RealSO101Backend 占位
  so101sim/tools.py        工具 API、安全层、工具 JSON schema
  so101sim/tasks.py        任务与评分器
  so101sim/logger.py       日志
  so101sim/agents/         openai_agent.py（Astra）、oracle.py、fake_client.py
  assets/so101/            SO-101 模型与网格（Apache-2.0，来自 TheRobotStudio）
  setup.sh, env.sh         环境安装；免 root 的 OSMesa 软件渲染（装到 .gl/，不入库）
```
