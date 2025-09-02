import datetime
import requests
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from google.adk.agents import Agent
from google.adk.tools import ToolContext

def get_json_data(city: str):
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
    API_KEY = "87ad902d24be999eed791156678a3ec7"
    url = BASE_URL + "appid=" + API_KEY + "&q=" + city + "&units=imperial"
    response = requests.get(url).json()
    print(response)
    return response

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    response = get_json_data(city)

    if response is None:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

    formatted_city = city.replace(' ', '_')

    print(f"formatted city {formatted_city}")

    tz_identifier = f"America/{formatted_city}"
    tz = None 

    try:
        tz = ZoneInfo(tz_identifier)
    except (ZoneInfoNotFoundError) as e:
        f"No time zone info found: "

    if tz is not None:
        now = datetime.datetime.now(tz)

        return {
            "status": "succes",
            "report": (
                f'The weather in {city} is {response["main"]["temp"]} but it feels like {response["main"]["feels_like"]}',
                'I was not able to find associated time zone information though'
                ),
        }

    return {
        "status": "succes",
        "report": (
               f'The weather in {city} is {response["main"]["temp"]} but it feels like {response["main"]["feels_like"]}',
               'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
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

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    if city.lower() == "chicago":
        tz_identifier = "America/Chicago"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    # model="gemini-2.0-flash-live-001",
    # model="gemini-2.0-flash-live-preview-04-09",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city. You MUST ask the user first if the city is in America, Europe, or Asia."
    ),
    # output_key="option",
    tools=[get_weather, get_current_time],
)
