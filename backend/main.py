from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="遥感目标智能检测平台",
    description="基于YOLO11的遥感图像目标检测系统API，支持飞机、油罐、立交桥、操场等目标检测",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health", tags=["健康检查"])
async def health_check():
    return {
        "status": "healthy",
        "service": "rsod-web-platform",
        "version": "1.0.0"
    }

@app.get("/", tags=["根路径"])
async def root():
    return {"message": "欢迎使用遥感目标智能检测平台"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
