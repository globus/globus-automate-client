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


cli_content = Content()
live_content = Live(cli_content, refresh_per_second=20)
