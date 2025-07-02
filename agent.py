from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, set_default_openai_client, set_default_openai_api
import asyncio,os

load_dotenv()
grok_cloud_api = os.getenv('grok_cloud_api')

client = AsyncOpenAI(base_url = "https://api.groq.com/openai/v1", api_key = grok_cloud_api)
set_default_openai_client(client,use_for_tracing=False)
set_default_openai_api("chat_completions",)

model = "llama-3.1-8b-instant"

agent =  Agent(
    name='Greeter',
    instructions='You greet the user and ask how you can help them today.',
    model=model,
)

async def result()-> str:
    result = await Runner.run(agent,input="Hello") 
    return result.final_output

if __name__ == "__main__":
    output = asyncio.run(result())
    print(output)