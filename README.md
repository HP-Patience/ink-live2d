# ink-live2d

墨像 Live2D 模型集。两个黑白风格模型，共用一套 PSD2Live 制作管线。

| 目录 | 模型 | 说明 |
|---|---|---|
| `InkPortrait/` | **InkPortrait** v6 | 黑白肖像。修正下睫毛跟随、耳朵重影与头顶轮廓，脖颈为上宽下窄的直线边缘，含独立后衣领 |
| `InkKeys/` | **InkKeys**（墨键） | 黑白 Q 版键鼠桌宠。黑发、方框眼镜、黑高领，手在键鼠上；按键联动蓝色高亮，适配 BongoCat 1.11+ |

两个模型都是真实 MOC3 网格，含表情、物理与动作参数，不是静态图片摆动效果。

## 目录结构

```
ink-live2d/
├── InkPortrait/
│   ├── models/InkPortrait/          # 运行时模型（moc3 + model3.json + 纹理）
│   ├── source/                      # 分层源文件、PSD、cmo3
│   ├── tools/                       # 制作脚本
│   ├── preview/                     # Cubism Web 预览
│   ├── validation/                  # 验证记录
│   └── docs/                        # 工作流与使用说明
└── InkKeys/
    ├── delivery/
    │   ├── InkKeys/                 # 运行时模型（含 key-layout.json 键位映射）
    │   ├── InkKeys-Live2D.zip       # 导入包
    │   └── InkKeys-Source.zip       # 源码包
    ├── source/                      # PSD、cmo3、分层素材
    ├── tools/                       # 制作脚本
    └── validation/                  # 验证记录与运行日志
```

## 共用管线

两个模型共用同一套上游工具链，版本锁定在各自的 `tools/toolchain.json`：

| 组件 | 版本 |
|---|---|
| PSD2Live（PSD → moc3 导出） | v0.7.1，SHA-256 校验 |
| SeeThrough（自动分层模型） | `seethroughv0.0.2_layerdiff3d_nf4` / `v0.0.1_marigold_nf4` |
| Cubism SDK for Web | 5-r.5 |
| Java / Python | 21 / 3.12 |

**`tools/setup_tools.py` 和 `tools/toolchain.json` 在两个模型下内容完全相同**（已逐字节比对）。升级 PSD2Live 版本时，两份需要同步替换，否则两个模型会用到不同版本的导出器。

`setup_tools.py` 会下载约 77 MB 的便携版工具到 `workspace/tools/`，并校验 SHA-256；`workspace/` 已加入 `.gitignore`，不入库。

## 构建

两个模型的流程一致，各自在目录内独立运行：

```bash
# 1. 准备工具链（首次执行，约 77 MB 下载）
cd InkKeys/tools && python setup_tools.py
cd ../../InkPortrait/tools && python setup_tools.py

# 2. 重新导出（从已提交的分层源文件，无需 GPU 重新推理）
cd InkKeys && python tools/rebuild.py
cd ../InkPortrait && python tools/rebuild.py
```

`rebuild.py` 调用 PSD2Live 的 Java 导出器（`BuildInkKeys.java` / `BuildPortrait.java`），产出 moc3 后重新打包并校验。InkPortrait 的 `rebuild.py` 还包含逐像素比对，确认 20 张图层能精确复现。

## 使用

**InkPortrait**：`models/InkPortrait/` 可直接被任意支持 Cubism 3+ 的运行时加载（Cubism Web、Live2D Viewer 等）。`preview/` 下有 Cubism Web 预览工程。

**InkKeys**：为 BongoCat 设计，键位映射在 `delivery/InkKeys/key-layout.json`。

```bash
# 方式一：导入 ZIP
#   BongoCat → 模型列表 → 导入 → 选择 InkKeys-Live2D.zip
# 方式二：放目录
#   把 delivery/InkKeys 整个文件夹复制到 <BongoCat 用户模型目录>/InkKeys，重新扫描模型
```

按键高亮逻辑：按下键盘时对应键帽蓝色高亮，`Ctrl+A` 等多个键同时按住会同时保持高亮，释放某个键只清除对应高亮；鼠标左右键也有独立高亮。

## 历史

两个目录通过 `git subtree` 导入，原始提交历史完整保留：

| 目录 | 来源 | 提交 |
|---|---|---|
| `InkKeys/` | 原 `ink-bongocat-live2d` 的 `artifacts/ruotengwu-live2d` | 3 条（含模型制作与按键高亮功能） |
| `InkPortrait/` | 原 `ink-portrait-live2d` | 6 条（v6 及 8 个肖像变体） |

`InkKeys/validation/` 下的验证记录产生于模型旧名 **Ruotengwu**（中文「若腾武」）时期，内容按原样保留作为证据快照，未做名字替换；改名事实见 `InkKeys/validation/RENAME-NOTE.md`。
