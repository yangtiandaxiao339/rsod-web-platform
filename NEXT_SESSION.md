# Next Session Handoff

更新时间：2026-05-20

## 当前项目状态

- Day 2 前端模板和基础联调已基本打通。
- `frontend` 已验证可构建通过。
- Day 3 后端训练链路代码已补齐，包含：
  - `backend/convert_rsod.py`
  - `backend/train_model.py`
  - `backend/upload_models_to_minio.py`
  - `backend/app/api/model.py`
  - `backend/app/services/minio_service.py`
  - `backend/app/utils/versioning.py`
  - `backend/data/rsod/yolo_dataset/rsod.yaml`
- 检测服务已调整为：
  - 有可用 YOLO 模型时走真实推理
  - 无模型或依赖不完整时可降级为 mock 结果
- 模型管理 API 已补充：
  - `GET /api/model/list`
  - `GET /api/model/current`
  - `POST /api/model/reload`

## 当前阻塞点

本地还没有 RSOD 训练数据集，以下目录目前需要你手动放入数据：

- `D:\rsod-web-platform\backend\data\rsod\images`
- `D:\rsod-web-platform\backend\data\rsod\annotations`

说明：

- `images` 里放原始图片，例如 `.jpg`
- `annotations` 里放对应同名 XML 标注文件
- 图片名和 XML 文件名必须一一对应

## `yolo11n.pt` 的作用

- `yolo11n.pt` 是 YOLO11 的预训练权重
- 训练 RSOD 时它作为初始化模型，用于迁移学习
- 它不是数据集，也不是最终业务模型
- 训练完成后会生成新的 `best.pt` / `last.pt`，这些才是你的 RSOD 微调结果

建议放置位置：

- `D:\rsod-web-platform\backend\models\rsod_yolo11n\weights\yolo11n.pt`

## 数据集下载来源

可手动下载 RSOD 原始数据集后再放到上面的目录：

- GitHub 项目页：`https://github.com/RSIA-LIESMARS-WHU/RSOD-Dataset-`
- Kaggle 镜像：`https://www.kaggle.com/datasets/hoseinyousefiya/rsod-dataset-original`

GitHub 页面里通常会给出百度网盘分卷链接，四类分别是：

- aircraft
- oiltank
- overpass
- playground

## 你把数据放好后，下一步直接执行

进入后端目录并激活环境：

```powershell
cd D:\rsod-web-platform\backend
conda activate rsod-web
```

1. 先做格式转换

```powershell
python convert_rsod.py
```

2. 检查是否生成 YOLO 数据集

```powershell
dir D:\rsod-web-platform\backend\data\rsod\yolo_dataset
```

3. 先做一次小规模训练冒烟测试

```powershell
python train_model.py --epochs 10 --batch 4 --device cpu
```

4. 如果流程正常，再决定是否上 GPU / 云端正式训练

```powershell
python train_model.py --epochs 100 --batch 16 --device 0
```

## 下次继续时建议直接告诉我

你下次打开后，直接发这两种任意一句就行：

- “读取 `NEXT_SESSION.md`，继续做 Day 3”
- “我已经把 RSOD 数据集放好了，继续检查并开始转换/训练”

## 距离项目整体完成还差什么

1. 下载并整理 RSOD 原始数据集到指定路径。
2. 运行 `convert_rsod.py`，确认标注转换正确。
3. 运行训练，产出 `best.pt`、日志、曲线图、评估结果。
4. 验证 MinIO 上传链路是否可用。
5. 用新模型替换当前检测服务加载逻辑，完成真实模型联调。
6. 做一次完整验收：
   - 前端上传图片
   - 后端真实推理
   - 模型列表接口
   - 模型切换/重载接口
   - 训练产物归档

## 风险提示

- 如果 RSOD 原始包里存在重名文件，解压后要先统一命名，再保证 XML 和图片同名。
- 如果 `ultralytics`、`torch`、`opencv-python` 版本不兼容，训练阶段可能需要重新校验依赖。
- CPU 训练只适合验证流程，不适合正式收敛训练。

## 2026-05-21 Progress Update

- Raw RSOD dataset has been placed successfully:
  - `backend/data/rsod/images`: 936 files
  - `backend/data/rsod/annotations`: 936 XML files
- Image/XML basename pairing was verified and matched.
- YOLO dataset conversion was completed:
  - train: 748
  - val: 188
- `rsod.yaml` is valid and points to:
  - `D:/rsod-web-platform/backend/data/rsod/yolo_dataset`
- Training environment issue was fixed:
  - old env had `ultralytics 8.0.200`
  - upgraded to `ultralytics 8.4.52`
- `conda run` hit a Windows encoding crash during training, so direct interpreter invocation is the reliable workaround:
  - `D:\Anaconda\envs\rsod-web\python.exe`
- `convert_rsod.py` was improved:
  - clamp out-of-range XML boxes to image bounds
  - skip invalid boxes
  - clear old generated `images/` and `labels/` on re-run
- 1-epoch CPU smoke test completed successfully after the fix:
  - run dir: `backend/models/runs/rsod-yolo11n_v1.0.2_20260521103955`
  - best model: `backend/models/releases/rsod-yolo11n-best_v1.0.2_20260521103955.pt`
  - last model: `backend/models/releases/rsod-yolo11n-last_v1.0.2_20260521103955.pt`
  - metrics:
    - mAP50: `0.526458`
    - mAP50-95: `0.233314`
    - precision: `0.770228`
    - recall: `0.466372`
    - f1: `0.580968`
- Label corruption warning is resolved:
  - train scan: `748 images, 0 corrupt`
  - val scan: `188 images, 0 corrupt`

## Immediate Next Steps

1. Run formal training on GPU instead of CPU.
2. Use a realistic training schedule, e.g. `epochs 100`, `imgsz 640`, `batch 16` if VRAM allows.
3. Review class imbalance/per-class metrics:
   - `overpass` is currently much weaker than the other classes.
4. Verify whether MinIO is actually available, then test model upload and model list APIs.
5. After a real trained model is accepted, switch backend inference to that trained RSOD model and do end-to-end frontend/backend validation.
