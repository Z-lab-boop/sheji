# CAD 与三维模型交付包

本目录提供三套比赛方案的可编辑 CAD、中性交换模型、3D 打印分件和制造辅助文件。

## 详细说明书

- 可编辑文档：`和氏璧杯_CAD与模型详细说明书.docx`
- 定稿 PDF：`../../output/pdf/和氏璧杯_CAD与模型详细说明书.pdf`
- 内容：方案定位、结构分解、关键尺寸、装配与动作逻辑、CAD 文件使用、参数修改、打样建议、验证记录及实体样机待验证项。
- 说明书中的尺寸与文件清单对应本目录现有 CAD 交付；“解围”的六个内装均为 68 × 62 × 44 mm 原创概念二次包装模块，不对应任何真实在售 SKU。

## 00 遂见——毛遂自荐青年名片匣

- 闭合包络：98 × 65 × 14 mm
- 机构：内托水平伸出 28 mm，名片抬升 7 mm
- 原生源文件：`suijian_card_case.FCStd`
- CAD 交换：`suijian_card_case.step`
- 3D 打印：`meshes/*.stl`
- 参数化重建：`build_product.py`

## 01 步步生典——邯郸双节漫游章匣

- 闭合包络：165 × 120 × 30 mm
- 模块：外壳、抽拉章盘、6 枚印章、印台盒、折叠地图代理件
- 原生源文件：`bubushengdian_stamp_kit.FCStd`
- CAD 交换：`bubushengdian_stamp_kit.step`
- 3D 打印：`meshes/*.stl`
- 参数化重建：`build_product.py`

## 02 解围——邯宝坊六味邯郸机关礼盒概念提案

- 闭合包络：290 × 230 × 75 mm
- 概念模块：6 件，单件 68 × 62 × 44 mm；分别对应鸡泽辣椒、魏县鸭梨、涉县核桃、武安小米、永年大蒜和大名小磨香油的原创二次包装提案
- 机关动作：侧向抽屉先移动 42 mm，中央托盘再抽出 145 mm
- 原生源文件：`jiewei_giftbox.FCStd`
- 三状态 CAD：`jiewei_giftbox_closed.step`、`jiewei_giftbox_unlocked.step`、`jiewei_giftbox_open.step`
- 3D 打印：`meshes/*.stl`
- 刀模：`dielines/*.dxf` 和 `dielines/*.svg`
- 参数化重建：`build_giftbox.py`、`build_dielines.py`、`design_config.py`

## 打开方式

- FreeCAD 1.1 或更高版本：打开 `.FCStd`。
- SolidWorks、Fusion 360、Rhino、Creo 等：导入 `.step`。
- Cura、PrusaSlicer、Bambu Studio 等：导入 `.stl`。
- AutoCAD、Illustrator 或包装刀模软件：打开 `.dxf`/`.svg`。

## 工程边界

交付文件已完成数字几何、尺寸、实体有效性和中性格式可读性检查。纸板摩擦、裱纸累积误差、满载强度、跌落、耐久与儿童安全尚需实体样机验证。
