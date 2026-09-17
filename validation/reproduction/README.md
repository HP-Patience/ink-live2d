# 仓库复现验证

2026-09-17：从已提交的自动分层重新运行修复及 Java 导出，20 张最终图层与保存版本逐像素相同。此目录的五份 JSON 是重新导出的模型在独立 Cubism Web 5-r.5 预览服务上的实际检查结果，不是复制历史报告。

环境：Python 3.12 / Java 21 / Node 24.16.0 / Playwright 1.58.2。默认浏览器下载在本机解压阶段停滞，实际检查通过 PLAYWRIGHT_CHROMIUM_EXECUTABLE 使用已有 Chromium 1243 构建。预览 TypeScript 与 Vite 生产构建通过；预览依赖锁文件执行 npm audit fix 后检查为 0 个已知漏洞（仅代表本次 npm 数据源的检查结果）。

导出日志保留原有几何偏差警告。检查脚本和运行方法见 [工具说明](../../docs/TOOLS.md)。
