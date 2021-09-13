from typing import Callable, Optional

from rich.console import RenderGroup
from rich.live import Live


class Content:
    """
    This class represents a per CLI invocation "canvas" which will hold the data
    that gets displayed on the CLI. All content updates happen by updating the
    value of the instance's RenderGroup
    """

    rg: RenderGroup = RenderGroup()

    def __rich__(self) -> RenderGroup:
        return self.rg


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


cli_content = Content()
live_content = PauseableLive(cli_content, refresh_per_second=20)
