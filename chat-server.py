import fastapi
import fastapi.staticfiles
import fastapi.responses
import fastapi.requests
import fastapi.routing

import uvicorn
import os
from langchain_ollama import ChatOllama

ollama_url = "http://192.168.39.136:11434"
model_name = "phi3.5"
model = ChatOllama(model=model_name,base_url=ollama_url)


## Hello server servlet using fastapi
app = fastapi.FastAPI()

## Chat server servlet using fastapi
## receives a message from the client using post json {"query":str} and returns the response
## Output reseponse in json format {"content":str}
@app.post("/chat")
async def chat(request: fastapi.Request):
    data = await request.json()
    query = data.get("query")
    response = model.invoke(query)
    return {"content": response.content}

#serve the static files on web folder  default index.html
app.mount("/", fastapi.staticfiles.StaticFiles(directory="web",html=True))
## Run the server

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

