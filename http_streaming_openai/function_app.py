"""
An Azure Function that interacts with Azure OpenAI and uses HTTP streaming. 
"""

import azure.functions as func
import openai
from azurefunctions.extensions.http.fastapi import Request, StreamingResponse
import asyncio
import os

# Azure Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

endpoint = os.environ["AZURE_OPEN_AI_ENDPOINT"]
api_key = os.environ["AZURE_OPEN_AI_API_KEY"]

# Azure Open AI
deployment = os.environ["AZURE_OPEN_AI_DEPLOYMENT_MODEL"]
temperature = 0.7

client = openai.AsyncAzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2023-09-01-preview"
)

# Get data from Azure Open AI
async def stream_processor(response):
    async for chunk in response:
        if len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if delta.content: # Get remaining generated response if applicable
                await asyncio.sleep(0.1)
                yield delta.content


# HTTP streaming Azure Function
@app.route(route="stream-cities", methods=[func.HttpMethod.GET])
async def stream_openai_text(req: Request) -> StreamingResponse:
    prompt = "List the 100 most populous cities in the United States."
    azure_open_ai_response = await client.chat.completions.create(
        model=deployment,
        temperature=temperature,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    return StreamingResponse(stream_processor(azure_open_ai_response), media_type="text/event-stream")