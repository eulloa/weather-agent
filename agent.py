from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import asyncio
import datetime
import os
import requests

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

load_dotenv()

# session management
session_service = InMemorySessionService()

def get_json_data(city: str):
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
    API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
    url = BASE_URL + "appid=" + API_KEY + "&q=" + city + "&units=imperial"
    response = requests.get(url).json()
    print(response)
    return response

def get_weather(city: str, tool_context: ToolContext) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    response = get_json_data(city)

    # TODO: tool_context logic below does not work as expected
    continent = tool_context.state
    print('!!! continent', continent)

    if response is None:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

    formatted_city = city.replace(' ', '_')

    print(f"formatted city {formatted_city}")

    # TODO: refactor time into it's own tool
    tz_identifier = f"America/{formatted_city}"
    tz = None 

    try:
        tz = ZoneInfo(tz_identifier)
    except (ZoneInfoNotFoundError) as e:
        f"No time zone info found: "
        tz = None

    if tz is not None:
        now = datetime.datetime.now(tz)

        return {
            "status": "succes",
            "report": (
                f'The weather in {city} is {response["main"]["temp"]} but it feels like {response["main"]["feels_like"]}',
                f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
                ),
        }

    return {
        "status": "succes",
        "report": (
               f'The weather in {city} is {response["main"]["temp"]} but it feels like {response["main"]["feels_like"]}',
               f'I was not able to find associated time zone information though'
            ),
    }

# def get_current_time(city: str, tool_context: ToolContext) -> dict:
#     """Returns the current time in a specified city.
#
#     Args:
#         city (str): The name of the city for which to retrieve the current time.
#
#     Returns:
#         dict: status and result or error msg.
#     """
#
#     continent = tool_context.state.get('option')
#
#     error = {
#         "status": "error",
#         "error_message": (
#             f"Sorry, I was not able to understand the content for {continent}."
#         ),
#     }
#
#     if not continent:
#         return error
#
#     formatted_city = city.lower().replace(' ', '_')
#
#     tz_identifier = f"America/{formatted_city}"
#     tz = ZoneInfo(tz_identifier)
#     now = datetime.datetime.now(tz)
#
#     if tz is None:
#         return error
#
#     report = (
#         f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
#     )
#     return {"status": "success", "report": report}

root_agent = LlmAgent(
    name="weather_time_agent",
    model=LiteLlm(model="ollama_chat/qwen3:latest"),
    # model="gemini-2.0-flash",
    # model="gemini-2.0-flash-live-001",
    # model="gemini-2.0-flash-live-preview-04-09",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city. You MUST ask the user first if the city is in America, Europe, or Asia. Before providing the time and weather, make sure you repeat the continent the user requests."
    ),
    # output_key="continent",
    tools=[get_weather],
)
