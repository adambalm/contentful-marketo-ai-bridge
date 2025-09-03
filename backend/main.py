from fastapi import FastAPI

app = FastAPI(title="Portfolio Backend API", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
