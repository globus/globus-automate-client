import time
from typing import Callable, Optional

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


class PauseableLive(Live):
    """
    We need this hack to prevent the underlying Live thread from rewriting
    stdout when we're attempting to get input from the user.
    """

    live_refresher: Optional[Callable] = None

    def pause_live(self):
        """
        Set the Live thread's refresh method to temporarily do nothing.
        """
        if self._refresh_thread is not None:
            self.live_refresher = self._refresh_thread.live.refresh
            self._refresh_thread.live.refresh = lambda *args: None

    def resume_live(self):
        """
        Restore the Live thread's refresh method allowing it to do its thing.
        """
        if self.live_refresher is not None:
            self._refresh_thread.live.refresh = self.live_refresher


cli_content = CLIContent(4)
live_content = PauseableLive(cli_content, refresh_per_second=20)
