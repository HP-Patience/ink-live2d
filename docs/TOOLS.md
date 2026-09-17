# 工具安装与复现

[返回首页](../README.md) · [制作流程](WORKFLOW.md)

完整制作 ZIP 已展开工具子模块；从 ZIP 使用时无需执行 git clone / git submodule 命令。Git 克隆方式仍须带 --recurse-submodules。

## 1. 固定输入重建：已实测

使用 Python 3.12、Java 21，在仓库根目录运行。依赖见 requirements.txt，固定工具版本见 [toolchain.json](../tools/toolchain.json)。不需要 GPU。

~~~bash
python -m pip install -r requirements.txt
python tools/setup_tools.py
python tools/rebuild.py
~~~

安装脚本从 PSD2Live 官方 Release 下载 0.7.1 portable ZIP，核验 SHA-256 后解压至 workspace/tools。不重传二进制；源码以固定提交子模块保留。如果已有 PSD2Live：

~~~bash
python tools/rebuild.py --psd2live-app /path/to/PSD2Live/app
# 仅重建 PSD 和 PNG，不调用 Java：
python tools/rebuild.py --source-only
~~~

最终结果在 workspace/repaired-v6 和 workspace/repaired-model-v6，日志在 workspace/rebuild.log。本次确认 20 张最终图层像素完全相同，并对重新导出的模型完成浏览器检查。

## 2. 本地网页预览：已实测

自行从 [Live2D 官方页面](https://www.live2d.com/en/sdk/download/web/) 获取 **Cubism SDK for Web 5-r.5**，阅读并遵守许可。不要把官方 Core 或完整 SDK 提交到本仓库。

使用支持 Vite 8 的 Node.js（本次为 Node 24.16.0）：

~~~bash
python tools/setup_preview.py --sdk /path/to/CubismSdkForWeb-5-r.5
cd workspace/sdk/Samples/TypeScript/Demo
npm ci
npm test
npm run build
npm start
~~~

打开 http://127.0.0.1:4174/ 。准备脚本将 SDK 复制到被 Git 忽略的 workspace/sdk，覆盖本项目示例文件，最后复制模型。**不要额外运行上游 copy_resources 命令**，以免覆盖模型资源。

预览刚重建的模型，可在仓库根目录运行：

~~~bash
python tools/setup_preview.py --sdk /path/to/CubismSdkForWeb-5-r.5 --model workspace/repaired-model-v6
~~~

左下角有手动面板。鼠标跟随只将歪头 ParamAngleZ 限幅至 ±12，与面板一致；左右转头和俯仰映射不变。开发服务器默认只绑定 localhost，不应直接暴露到公网。

## 3. 回归检查：已实测

保持预览运行，在另一终端回到仓库根目录：

~~~bash
npm ci
npx playwright install chromium
npm run test:browser
python tools/verify_delivery.py
~~~

浏览器默认检查 http://127.0.0.1:4174/ ，可用环境变量 PREVIEW_URL 指定其他端口。输出 JSON 和姿态截图在 workspace。浏览器已安装时，可用 PLAYWRIGHT_CHROMIUM_EXECUTABLE 指定兼容 Chromium 可执行文件；本次复现使用本机已有 Chromium。脚本执行本仓库的可信测试代码，不要替换为来源不明的脚本。

交付检查覆盖关键资产哈希、模型引用、验证记录、文档链接、文件大小与已知敏感信息模式。这是防误提交检查，不是全面安全审计。

## 4. GPU 重新分层：可选、非一键保证

最终模型复现**不依赖此步骤**。保存了制作时的推理入口；打包阶段未重新下载权重或再跑一次 GPU 推理。

~~~bash
git submodule update --init --recursive
# 在独立 CUDA 环境安装 vendor/see-through 的上游依赖与 NF4 所需依赖
# 根据显卡/驱动选择兼容的 PyTorch、CUDA、bitsandbytes
python tools/infer.py
~~~

- 根目录 requirements.txt 只覆盖 CPU 图层修复，不是完整 GPU 环境锁文件。
- [原推理环境记录](../validation/inference-environment-observed.txt) 是已安装包的观察记录，不是跨平台安装承诺。
- infer.py 核验并应用 [NF4 补丁](../patches/see-through-nf4.patch)，随后下载两个 Hugging Face 权重仓库。会使 See-through 子模块出现预期的本地修改。
- 权重未上传，也未锁定 HF revision；重新推理不保证与保存结果完全相同。
- 输出在 workspace/new-inference，不覆盖保存输入。修复脚本依赖本张肖像的部件名与坐标；新人物或新推理输出需要重新适配。
- 原始推理使用 NF4，分层分辨率 1280、深度 768。历史单次峰值显存约 4.03 GB、总耗时约 659 秒，**不是通用最低硬件或性能承诺**。

## 脚本分工

| 文件 | 用途 |
|---|---|
| repair_portrait.py | 重建脸、眼部、颈部与衣服等基础部件 |
| fix_portrait_layers.py | v2：清除后发重复耳朵及浅色残留 |
| fix_portrait_v3.py | 扩展顶部画布、低弧度头顶，恢复脖颈 |
| fix_portrait_v4.py / fix_portrait_v5.py | 历史方案，不进入最终构建链 |
| fix_portrait_v6.py | 直线收窄脖颈、独立后衣领；包含像素与几何断言 |
| BuildPortrait.java | 调用 PSD2Live，设置下睫毛父变形器 |
| rebuild.py | 串联最终流程，核验全部最终图层 |
