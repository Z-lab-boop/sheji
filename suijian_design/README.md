# 遂见 · 毛遂自荐青年名片匣

本目录是 2026“和氏璧杯”赛道二参赛设计的独立、可复现工程。

## 构建入口

- 设计参数：`scripts/design_config.py`
- 参数化模型：`03_cad/build_product.py`
- 产品渲染：`04_renders/render_product.py`
- 视觉资产：`scripts/build_identity.py`
- 参赛展板：`scripts/build_boards.py`
- 投稿审计：`scripts/audit_submission.py`

所有生成文件必须经过 `tests/` 与 `07_audit/audit_report.json` 验证。工程不修改同级目录中既有的短视频作品。

