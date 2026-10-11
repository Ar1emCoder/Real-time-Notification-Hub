from fastapi import FastAPI

app = FastAPI(title="Real-time Notification Hub")


@app.get("/health")
def health_check():
    return {"status": "Живой!"}