from fastapi import FastAPI
from app.routers import events

app = FastAPI(title="Real-time Notification Hub")


@app.get("/health")
def health_check():
    return {"status": "Живой!"}


app.include_router(events.router)  # регистрация роутера