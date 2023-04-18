import json
import os
import tempfile

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask

app = FastAPI()

_TODOS = {}


@app.get("/")
async def ping():
    """A ping endpoint for health check. Expected to return 'pong' as a response.
    """
    return "pong"


@app.get("/help")
async def help():
    """Generic /help endpoint to return a help message on how to use the Plugin.
    """
    return "This TODO plugin add, get, and delete todo lists for individual users"


@app.post("/todos/{username}")
async def add_todo(username: str, todo: str):
    """Adds one todo to a username.
    """
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(todo)
    return JSONResponse(content='OK', status_code=200)


@app.get("/todos/{username}")
async def get_todos(username: str):
    """Gets todo for a specific user.
    """
    return JSONResponse(content=_TODOS.get(username, []), status_code=200)


@app.delete("/todos/{username}")
async def delete_todo(username: str, todo_idx: int):
    if username in _TODOS and 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return JSONResponse(content='OK', status_code=200)


@app.get("/logo.png")
async def plugin_logo():
    """Returns logo
    """
    return FileResponse('logo.png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest(request: Request):
    """Returns the ai-plugin.json manifest.
    """
    host = request.headers['host']

    with open(".well-known/ai-plugin.json") as f:
        text = f.read().replace("PLUGIN_HOSTNAME", f"https://{host}")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(text.encode())
        temp_file_path = temp_file.name

    def cleanup():
        os.remove(temp_file_path)

    response = FileResponse(temp_file_path, background=BackgroundTask(cleanup))
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
