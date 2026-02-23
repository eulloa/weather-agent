from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.agents import LoopAgent 
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import google_search

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

load_dotenv()

# session management
# session_service = InMemorySessionService()

time_agent= LlmAgent(
        name="time_agent",
        model="gemini-2.5-flash",
        instruction="Use the google_search tool to look up the time for the desired city",
        description="A helpful agent focused on providing the time for a specific city",
        tools=[google_search],
        output_key="time_result"
)

weather_agent= LlmAgent(
        name="weather_agent",
        model="gemini-2.5-flash",
        instruction="Use the google_search tool to look up the weather for the desired city",
        description="A helpful agent focused on providing the weather for a specific city",
        tools=[google_search],
        output_key="weather_result"
)

weather_report_agent = LlmAgent(
        name="weather_report_agent",
        model="gemini-2.5-flash",
        instruction="""Read and form a detailed weather report based on the time from state['time_result'] and the weather data from state['weather_result']. Create a brief weather report and provide it to the user based on this data""",
        tools=[google_search],
        description="Generates a detailed weather report",
)

root_agent = LoopAgent(
    name="reporter_agent",
    max_iterations=3,
    sub_agents=[
       time_agent,
       weather_agent,
       weather_report_agent
    ]
)

