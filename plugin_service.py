from semantic_kernel.functions import kernel_function
import chainlit as cl


class DateTimePlugin:
    """A plugin to get the current date and time."""

    @cl.step(type="tool")
    @kernel_function(description="Get the current date and time.")
    def get_current_date(self) -> str:
        """Get the current date and time."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
