from fastapi import FastAPI

app = FastAPI(
    title="AI Legal Ops Gateway",
    description="Multi-tenant middleware for AI orchestration with privacy enforcement",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "AI Legal Ops Gateway is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
