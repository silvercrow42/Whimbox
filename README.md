![logo](/docs/logo.png)
~~不会画画，先放个红温星在这里凑合一下~~
# Whimbox · 奇想盒
Whimbox，基于大语言模型和图像识别技术的AI智能体，辅助你游玩无限暖暖！

## 如何运行
（启动器已经上线，也可以通过启动器一键运行，[启动器项目地址](https://github.com/nikkigallery/WhimboxLauncher)）
1. 本项目仅支持python3.12，请先自行下载安装
2. 下载Releases中的最新whl包
3. 一键安装刚刚下载的whl包
```shell
pip install whimbox-x.x.x-py3-none-any.whl
```
2. 运行如下命令，初始化项目，会自动创建configs，scripts文件夹
```
whimbox init
```
3. 修改`configs/congfig.json`中的Agent配置，为自己的大模型接口
```json
    "Agent": {
        "model": {
            "value": "Qwen/Qwen3-30B-A3B-Instruct-2507",
            "description": "模型名称"
        },
        "model_provider": {
            "value": "openai",
            "description": "模型提供商"
        },
        "base_url": {
            "value": "https://api.siliconflow.cn/v1/",
            "description": "模型API地址"
        },
        "api_key": {
            "value": "",
            "description": "模型API密钥"
        }
    },
```
4. 将 [跑图路线仓库](https://github.com/nikkigallery/WhimboxScripts) 中的路线脚本下载下来，放到`scripts`目录里
5. 打开游戏，将游戏设置为窗口模式，分辨率1920*1080
6. 用管理员权限运行如下命令，启动奇想盒
```shell
whimbox
```
7. 程序运行后请稍等片刻。在游戏界面的左侧看到窗口后，按`/`打开对话框，按`esc`关闭对话框

## 已有功能
* 每日任务
    * 美鸭梨挖掘
    * 素材激化幻境
    * 闪光祝福幻境
    * 检查朝夕心愿
    * 领取大月卡
    * 朝夕心愿一条龙
* 自动跑图
    * 跑图路线录制、编辑
    * 自动跑图（暂时只支持大世界和星海）
    * 自动采集、捕虫、清洁、钓鱼
* AI对话
    * 通过自然语言编排以上所有功能
    * 随时中断任务

## 未来计划
1. 框架完善：回退机制。
2. 多地图适配
3. 自动战斗
4. 自动弹琴（我必须立刻演奏春日影！）
5. 自动星海和家园

## 注意事项
* Whimbox不会修改游戏文件、读写游戏内存，只会截图和模拟鼠标键盘，理论上不会被封号。但游戏的用户条款非常完善，涵盖了所有可能出现的情况。所以使用Whimbox导致的一切后果请自行承担。
* 由于游戏本身已经消耗PC的大量性能，图像识别还会额外消耗性能，所以目前仅支持中高配PC运行，功能完善后会开发云游戏版本。
* Whimbox目前仅支持1920x1080窗口模式运行的游戏。

## 致谢
感谢各个大世界游戏开源项目的先行者，供Whimbox学习参考。
* [原神小助手·GIA](https://github.com/infstellar/genshin_impact_assistant)
* [更好的原神·BetterGI](https://github.com/babalae/better-genshin-impact)

感谢chatgpt、cursor、claude等各种AI模型和AI编程工具

## 加入开发
项目还有大量功能需要开发和适配。如果你对此感兴趣，欢迎加入一起研究。开发Q群：821908945。

### 项目结构
```
Whinbox/
├── whimbox/                        
│   ├── ability/                  # 能力切换模块
│   ├── action/                   # 动作模块（拾取、钓鱼、战斗等等）
│   ├── api/                      # ocr，yolo等第三方模型
│   ├── assets/                   # 地图、UI截图、游戏图标、配置文件等资源
│   ├── common/                   # 公共模块（日志、工具等等）
│   ├── config/                   # 配置模块
│   ├── dev_tool/                 # 开发工具
│   ├── ingame_ui/                # 游戏内聊天框
│   ├── interaction/              # 交互核心模块（截图、操作）
│   ├── map/                      # 地图模块（小地图识别，大地图操作）
│   ├── task/                     # 任务模块（各种功能脚本，供mcp调用）
│   ├── ui/                       # 游戏UI模块（页面、UI）
│   ├── view_and_move/            # 视角和移动模块
│   ├── main.py                   # 程序入口
│   ├── mcp_agent.py              # 大模型agent
│   └── mcp_server.py             # MCP服务器
├── configs/                      # 配置文件（首次运行会自动生成）
│   ├── config.json               # 项目的配置文件
│   └── prompt.txt                # 大模型提示词
├── scripts/                      # 自动跑图的脚本仓库（首次运行会自动生成）
├── logs/                         # 日志文件
└── build.bat                     # 一键打包
```
### MCP工具编写
可参考`source\task\daily_task`内的几个task，并在`source\mcp_server.py`中注册，就能被大模型调用。

### 跑图路线录制
详情请查看 [跑图路线仓库](https://github.com/nikkigallery/WhimboxScripts)
