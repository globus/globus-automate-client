import threading

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

    lock = threading.RLock()

    def __enter__(self):
        super().__enter__()
        original_refresh = self._refresh_thread.live.refresh

        def replacement_refresh():
            with self.lock:
                return original_refresh()

        self._refresh_thread.live.refresh = replacement_refresh

    def pause_live(self):
        """Pause live rendering.

        This is accomplished by acquiring the lock that the refresh thread depends on.
        Although it's a re-entrant lock, only the main thread is able to release it.
        """
        self.lock.acquire()

    def resume_live(self):
        """Unpause live rendering."""
        self.lock.release()


cli_content = Content()
live_content = PauseableLive(cli_content, refresh_per_second=20)
