<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="ink-live2d：墨像 Live2D 模型集，包含 InkPortrait 肖像与 InkKeys 键鼠桌宠">
</p>

<p align="center">
  <strong>两个黑白 Live2D 模型：InkPortrait 肖像与适配 BongoCat 的 InkKeys 键鼠桌宠。</strong><br>
  模型、源文件、制作脚本和验证记录按目录交付；InkPortrait 的网页预览需要另行准备官方 Cubism SDK。
</p>

<p align="center">
  <a href="https://github.com/HP-Patience/ink-live2d"><img src="https://img.shields.io/github/stars/HP-Patience/ink-live2d?style=flat-square" alt="GitHub stars"></a>
  <a href="https://github.com/HP-Patience/ink-live2d/commits/main"><img src="https://img.shields.io/github/last-commit/HP-Patience/ink-live2d?style=flat-square" alt="最近提交"></a>
  <a href="https://github.com/HP-Patience/ink-live2d/issues"><img src="https://img.shields.io/github/issues/HP-Patience/ink-live2d?style=flat-square" alt="开放 issue"></a>
  <a href="https://github.com/HP-Patience/ink-live2d"><img src="https://img.shields.io/badge/models-2-111111?style=flat-square" alt="模型数量：2"></a>
  <a href="https://github.com/HP-Patience/ink-live2d"><img src="https://img.shields.io/badge/format-Live2D-555555?style=flat-square" alt="格式：Live2D"></a>
</p>

## 效果展示

### InkPortrait · 黑白肖像

![InkPortrait v6 的 Cubism Web 实际运行录像](InkPortrait/docs/images/InkPortrait-v6-preview.gif)

### InkKeys · 键鼠桌宠

![InkKeys 在 BongoCat 中的实际运行效果](InkKeys/delivery/InkKeys-BongoCat-preview.gif)

以上为仓库已有运行录像；InkPortrait 录像中的背景属于历史预览，新版网页预览已去掉教室背景。

## 模型与交付

| 目录 | 模型 | 已核对的内容 |
|---|---|---|
| [`InkPortrait/`](InkPortrait/) | **InkPortrait v6** | 黑白肖像 MOC3、PSD/CMO3、20 个最终部件；含下睫毛跟随、耳朵重影、头顶轮廓和后衣领修复。 |
| [`InkKeys/`](InkKeys/) | **InkKeys（墨键）** | BongoCat 1.11+ 交付包；真实 MOC3 网格、逐键键位落点与蓝色高亮、鼠标左右键反馈。 |

两个模型都包含表情、物理与动作参数，不是静态图片摆动效果。对应的运行截图、日志和回归记录保存在各自的 `docs/` 或 `validation/` 中。

## InkPortrait：网页预览

预览支持**鼠标悬停跟随**，无需按住拖动；移出画布后视线回正。教室背景已移除，画布透明，浏览器中透出页面底色；左下角可切换自动动作与手动参数控制。

仓库不分发专有的 Cubism Core 或完整官方 SDK。要运行本项目修改过的官方 Demo，先从 [Live2D 官方网站](https://www.live2d.com/en/sdk/download/web/) 获取 **CubismSdkForWeb-5-r.5** 并遵守许可，准备 Node.js、npm 与 Python，再执行：

```bash
cd InkPortrait
python tools/setup_preview.py --sdk /path/to/CubismSdkForWeb-5-r.5
cd workspace/sdk/Samples/TypeScript/Demo
npm ci
npm start
```

预览地址：<http://127.0.0.1:4174/>。此预览工程是本项目对官方 SDK Demo 的覆盖，不是完整开箱即用应用；浏览器运行不会自动替代 VTube Studio 的摄像头实测。

直接使用模型时，保留 `InkPortrait/models/InkPortrait/` 的完整相对路径；详细导入步骤、建议参数和限制见 [`InkPortrait/docs/USAGE.md`](InkPortrait/docs/USAGE.md)。

## InkKeys：导入 BongoCat

将 [`InkKeys/delivery/InkKeys-Live2D.zip`](InkKeys/delivery/InkKeys-Live2D.zip) 导入 BongoCat，或把 [`InkKeys/delivery/InkKeys/`](InkKeys/delivery/InkKeys/) 整个目录复制到用户模型目录后重新扫描。

- 鼠标移动：头部、视线和鼠标手跟随；左右键有独立按压反馈。
- 键盘：按标准 QWERTY 键位移动键盘手，并高亮对应键帽；释放后归位。
- 空闲：眨眼、呼吸和头发物理由 Live2D 网格驱动。
- BongoCat 1.11.0 的限制：主 Enter 与数字小键盘 Enter 都报告为 `Return`，两侧 Windows 键都报告为 `Meta`，皮肤无法区分；F13–F24 使用功能行替代位置。

交付包内的 `resources/left-keys/` 是逐键资源，不要删除；验证说明见 [`InkKeys/delivery/使用说明.md`](InkKeys/delivery/使用说明.md)。

## 目录结构

```text
ink-live2d/
├── InkPortrait/
│   ├── models/InkPortrait/          # 运行时模型（moc3 + model3.json + 纹理）
│   ├── source/                      # PSD、CMO3 与分层源文件
│   ├── tools/                       # 制作、重建与预览脚本
│   ├── preview/                     # 官方 SDK Demo 覆盖文件
│   ├── validation/                  # 验证记录
│   └── docs/                        # 工作流与使用说明
└── InkKeys/
    ├── delivery/                    # BongoCat 导入包、运行模型与中文说明
    ├── source/                      # PSD、CMO3、分层素材与键位配置
    ├── tools/                       # 打包与验证脚本
    └── validation/                  # 运行日志与证据快照
```

## 共用制作管线

两个模型的工具链版本锁定在各自的 `tools/toolchain.json`：

| 组件 | 版本 |
|---|---|
| PSD2Live（PSD → moc3） | v0.7.1，SHA-256 校验 |
| SeeThrough（自动分层） | `seethroughv0.0.2_layerdiff3d_nf4` / `v0.0.1_marigold_nf4` |
| Cubism SDK for Web | 5-r.5（本地预览另行获取） |
| Java / Python | 21 / 3.12 |

从已提交的分层源文件重建时无需 GPU 重新推理；工具下载到被忽略的 `workspace/`，不会进入仓库。两个目录的 `setup_tools.py` 与 `toolchain.json` 已保持一致，升级导出器时需同步替换。

```bash
cd InkKeys/tools && python setup_tools.py
cd ../../InkPortrait/tools && python setup_tools.py
cd ../../InkKeys && python tools/rebuild.py
cd ../InkPortrait && python tools/rebuild.py
```

## 历史与限制

两个目录通过 `git subtree` 导入并保留原始提交历史：`InkKeys/` 来自原 `ink-bongocat-live2d` 的 `artifacts/ruotengwu-live2d`，`InkPortrait/` 来自原 `ink-portrait-live2d`。`InkKeys/validation/` 中的旧名 **Ruotengwu** 是历史验证快照，改名说明见 [`InkKeys/validation/RENAME-NOTE.md`](InkKeys/validation/RENAME-NOTE.md)。

这些交付物针对固定素材和已核对运行环境制作，不承诺任意图片自动生成商业精绑模型，也不承诺所有摄像头、播放器或 BongoCat 版本行为一致。原画、模型与第三方工具的权利分别处理，不能把整仓库视为 MIT；详情见 [权利与第三方许可](InkPortrait/docs/RIGHTS.md)。
