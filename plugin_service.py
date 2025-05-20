from semantic_kernel.functions import kernel_function, KernelArguments
import chainlit as cl


class WeatherPlugin:
    """Plugin to get weather information."""

    def __init__(self):
        pass

    @cl.step(type="tool")
    @kernel_function(description="Get weather information for a city.")
    def get_weather_info(self, city: str) -> str:
        """Get weather information for a given city."""
        # Simulate a call to a weather API
        return f"The forecast for {city} today is sunny, with temperatures climbing to 25°C."
