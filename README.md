# lichess-bot-gui，版本1.2
本项目基于lichess-bot项目二次开发，使用AGPL协议
原项目：[点击进入原项目](https://github.com/lichess-bot-devs/lichess-bot)

# 开源协议合规说明
1. 本项目整体协议：GNU Affero General Public License v3.0 (AGPLv3)
2. 声明：因基于 AGPLv3 上游项目衍生，根据开源协议条款，全部代码强制保持 AGPLv3 开源，不可闭源商用、不可修改协议
3. AGPL 特殊条款提示：
    若你将本项目部署为公网在线服务（网站、API、SaaS），必须向所有网络访问者提供完整源码（仓库地址 / 下载入口）
    分发、修改、二次衍生项目，整体代码必须延续 AGPLv3，禁止转为 MIT/Apache/ 私有闭源

# 项目主要功能说明
- 以lichess-bot为基础，增加支持中文
- 增加了GUI的一些组件
- 完整更新日志在update_log.md
- 更多内容[点击查看详情](https://github.com/lichess-bot-devs/lichess-bot)

# 使用教程

## 一、前置硬性要求（必看）
1. **全新 Lichess 账号**
    不能下过任何对局、不能发消息，否则无法转为 Bot 账号。
2. Python 3.7+（推荐3.10/3.11）
3. 国际象棋引擎（主流 Stockfish 16+，免费最强）
4. 网络可访问 lichess.org

## 二、注册并升级Bot账号
### 2.1 新建账号
打开 https://lichess.org/signup ，注册独立机器人账号，**不要下任何棋**。

### 2.2 生成API Token（关键）
1. 进入令牌创建页：https://lichess.org/account/oauth/token/create
2. 权限勾选 **bot:play**（必须），可额外勾选 `challenge:write`
3. 描述随便填（如 StockfishBot），点击创建
4. 复制 `lip_xxxx` 令牌，**只显示一次，妥善保存，切勿泄露**

### 2.3 将账号升级为Bot身份（二选一）
```bash
curl -X POST https://lichess.org/api/bot/account/upgrade -H "Authorization: Bearer 你的lip_令牌"
```
返回 `{"ok":true}` 即升级成功。

## 三、安装Python依赖
1. 打开 CMD/PowerShell（Windows）/Terminal（Mac/Linux），进入项目文件夹
2. 安装依赖：
```bash
# 升级pip
python -m pip install --upgrade pip
# 批量安装所需库
pip install -r requirements.txt
```

## 四、下载国际象棋引擎 Stockfish
1. 官网下载对应系统二进制：https://stockfishchess.org/download/
    - Windows：Windows x86-64 exe
    - Mac：Apple Silicon / Intel 版本
    - Linux：Linux x86-64
2. 解压，把 `stockfish.exe` / `stockfish` 放进本项目的src/engines文件夹，记住路径。

## 五、配置 config.yml（核心配置）
> 方法1：进入src文件夹，打开config.yml文件
>
> 方法2：见下文：`修改配置相关其他内容`

### ① 填入API令牌
```yaml
token: "lip_你的完整令牌"
```

### ② 引擎路径（engine）
```yaml
engine:
  # Windows示例
  engine_path: "./stockfish.exe"
  # Mac示例
  # engine_path: "./stockfish-macos-arm64"
  # Linux示例
  # engine_path: "./stockfish-linux-x64"
```

### ③ 引擎强度（uci_options，自由调节）
```yaml
uci_options:
  Threads: 4          # CPU核心数，根据电脑改
  Hash: 1024          # 缓存MB，内存大可以2048/4096
  Skill Level: 20     # 0最弱，20满强度
  Move Overhead: 500  # 防超时，网络差改800
```

### ④ 对局过滤（接受/拒绝挑战）
```yaml
challenge:
  enabled: true
  accept_bot: true    # 是否接受其他机器人挑战
  accept_human: true   # 是否接受人类玩家
  min_rating: 0
  max_rating: 3500
  time_controls:       # 支持的时限
    - bullet
    - blitz
    - rapid
    - classical
```

### ⑤ 其他常用配置
```yaml
# 自动发起挑战
matchmaking:
  enabled: false # 想自动找人对战改为true
  variant: standard
  time_class: blitz
```

## 六、启动机器人
> run_bot_without_gui是没有GUI，直接运行lichess-bot的
>
> run_gui是启动整个GUI工具

- windows用户直接双击运行首页的bat文件
- macos/linux用户先添加执行权限，然后再运行首页的sh文件

以下是macos/linux用户添加执行权限的命令
```bash
chmod +x run_gui.sh
chmod +x run_bot_without_gui.sh
```

### 启动成功标志
控制台输出：
`Logged in as @你的Bot用户名`
`Waiting for challenges...`

此时打开 https://lichess.org/@你的Bot名，头像旁显示**绿色在线圆点**，其他人即可发起挑战。

### 停止机器人
直接关闭终端窗口 / Ctrl+C。

## 七、常见报错与解决
1. **FileNotFoundError: config.yml**
    未复制 `config.yml.default` → 重命名为 `config.yml`。

2. **YAML语法报错**
    yml缩进必须用**2个空格**，不能用Tab；冒号后必须加空格；不要中文符号。

3. **Engine not found**
    `engine_path` 路径写错；引擎文件放错文件夹；Windows权限不足。

4. **Bot账号未升级，API返回400**
    账号下过棋无法升级，必须新建空白账号；重新执行升级Bot命令。

5. **对局频繁超时**
    提高 `Move Overhead`（改为800~1000）；降低Threads/Hash减轻CPU负载。

6. **不接受任何人挑战**
    config.yml中 `challenge.enabled` 设为true；检查 `accept_human/accept_bot`。

7. **token权限不足**
    重新创建token，务必勾选 `bot:play`。

## 八、进阶优化
1. **开局库（Opening Book）**
    在engine配置添加 `book: true`，填入epd/pgn开局库路径，减少思考时间。
2. **残局库（Tablebase）**
    下载Syzygy残局库，配置 `syzygy_path`，残局走棋更完美。
3. **24小时挂机**
    Windows：nssm把程序注册为系统服务；
    Linux/Mac：screen/tmux后台运行；云服务器长期托管。
4. **限制只能人类对战**
    `accept_bot: false`，关闭机器人互下。

## 九、重要规则提醒
1. 禁止用Bot代打人类天梯，Lichess检测到会永久封禁账号；
2. Token不要上传GitHub、不要发给他人；
3. 机器人仅用于练棋、测试引擎，遵守平台用户协议。

# 修改配置相关其他内容
> 开始运行gui_main.py的时候会弹出一个启动配置对话框
>
> 可以自由勾选各个组件，每个组件对应一个功能
>
> 修改完成后重启生效

## `修改机器人配置`组件，用来修改config.yml
- 详细信息请参照：`使用教程-→五、配置 config.yml（核心配置）`

## `修改该程序配置`组件，用来修改gui_config.json
- 用处：GUI程序的一些配置
- json不能注释，所以修改方式请参照下方的`gui_config.json配置修改说明`

## `修改该程序样式`组件，用来修改style.txt
- 用处：主窗口的样式
- 格式请参照qt样式表的格式

# gui_config.json配置修改说明

## chess.svg.board()尺寸与样式
- **`size`**
    棋盘像素大小（正方形），例如 `400` → 400×400，默认 `None`（无限制）。

- **`coordinates`**
    是否显示棋盘坐标（a-h / 1-8），默认 `True`，设 `False` 关闭。

- **`colors`**
    自定义棋盘颜色（覆盖默认配色）。
    可用键：
    - `square light` / `square dark`：浅色/深色格子
    - `square light lastmove` / `square dark lastmove`：最后一步高亮
    - `margin` / `coord`：边距、坐标颜色
    - `arrow green/blue/red/yellow`：箭头颜色
    颜色格式：`#ffce9e`（不透明）、`#15781B80`（带透明通道）

- **`flipped`**
    翻转棋盘（黑方在下），设 `True` 开启。

- **`borders`**
    显示棋盘外边框，默认 `False`，设 `True` 开启。

## game_viewer要观看的账号
修改`game_viewer_user_name`项目为将要观战的账号