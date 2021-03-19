import time
from typing import Optional

from rich.console import RenderGroup
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text


class CLIContent:
    """
    A rich renderable class that displays CLI content.

    Depending on when the state of this object it will either display nothing
    (in the case that it was never updated), text only (in the case that its
    content will stop getting updated), or text and a spinner (in the case that
    it will periodically receive updated content to display).

    Additionally, this class functions as a counter to indicate when it expects
    to get its text content updated. This ensures that the renderable is only
    updated at a fixed interval, instead of on every refresh.
    """

    spinner: Spinner = Spinner("simpleDotsScrolling")
    last_update: Optional[float] = None
    text: Text = Text()
    done = False

    def __init__(self, interval: int):
        self.interval = interval

    def time_to_update(self):
        """
        Track how often updates to the CLIContents should be made.
        """
        now = time.time()
        if self.last_update is None or now - self.last_update >= self.interval:
            return True
        return False

    def update(self, text: Text):
        """
        Update the object's text output. This will cause the CLIContent to begin
        displaying a spinner indicating updates are incoming.
        """
        self.last_update = time.time()
        self.text = text

    def init(self):
        """
        Prepare the object to begin receiving updates.
        """
        self.done = False

    def complete(self):
        """
        Set the object's state to indicate that it will no longer receive
        updates.
        """
        self.done = True

    def __rich__(self) -> Text:
        """
        The dunder method for the rich protocol which gets called on refresh.
        """
        # If last_update is None, that means this instance has nothing to
        # render, so omit the spinner.
        if self.last_update is None:
            return self.text

        # If the CLIContent will no longer receive updates, omit the spinner.
        if self.done:
            return self.text

        return RenderGroup(self.text, self.spinner)


cli_content = CLIContent(4)
live_content = Live(cli_content, refresh_per_second=20)
