# 版本演进

[返回首页](../README.md)

**下载使用 v6；v1–v5 仅供历史过程对照，不是推荐模型。**

| 版本 | 修改 | 展示 |
|---|---|---|
| v1 | 基础修复、绑定与首版实际 Live2D 导出 | [多姿态](history/InkPortrait-poses.jpg) |
| v2 | 下睫毛绑定眼睛变形器；清除后发耳朵残影 | [修复对比](history/InkPortrait-v2-fix-comparison.jpg) |
| v3 | 恢复脖颈；头顶降低弧度，避免过度上凸 | [对比](history/InkPortrait-v3-fix-comparison.jpg)、[组合姿势](history/InkPortrait-v3-combined-poses.jpg) |
| v4 | 尝试消除右侧颈部露边，曲线轮廓不合需求 | [历史对比](history/InkPortrait-v4-neck-comparison.jpg) |
| v5 | 脖颈改为直边，但倾斜方向仍需调整 | [历史对比](history/InkPortrait-v5-neck-comparison.jpg) |
| **v6** | **上宽下窄的直线脖颈 + 独立后衣领** | [最终对比](images/InkPortrait-v6-neck-comparison.jpg)、[最终姿态](images/InkPortrait-v6-poses.jpg) |

鼠标歪头限幅属于播放器修复，保留至最终版，只影响 ParamAngleZ，并非缩小整个模型的参数范围。

[历史 GIF](history/InkPortrait-preview.gif) 和 [历史 MP4](history/InkPortrait-preview.mp4) 均为 **v1**；首页使用重新录制的 **v6**。历史日志与运行记录在 [validation](../validation)，历史模型包在 [v6 Release 附件](https://github.com/HP-Patience/ink-portrait-live2d/releases/tag/v6.0.0)，文件名注明版本。

最终构建链：**基础修复 → v2 → v3 → v6**，不执行已否定的 v4/v5 脖颈方案。
