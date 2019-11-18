from fastapi import FastAPI

app = FastAPI()


@app.post("/query")
async def query_entrypoint(query_data):
    return {"test": query_data}
