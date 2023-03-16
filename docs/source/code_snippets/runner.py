import logging
import os
import pathlib
import queue
import sys

# The flow to run.
FLOW_ID = "your-flow-id-here"

# The flow will be run X seconds after the most recent filesystem event is received.
# If no filesystem events are ever received, the flow will not be run.
COOL_OFF_TIME_S = 60


logging.basicConfig(
    level=logging.WARNING,  # Eliminate INFO messages from the Globus SDK.
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

try:
    from globus_automate_client import create_flows_client
except ImportError:
    log.error(
        "The globus_automate_client package is not installed."
        " (Do you need to activate a virtual environment?)"
    )
    sys.exit(1)

try:
    import watchdog
    import watchdog.events
    import watchdog.observers
except ImportError:
    log.error(
        "The watchdog package is not installed."
        " (Do you need to activate a virtual environment?)"
    )
    sys.exit(1)


class Handler(watchdog.events.FileSystemEventHandler):
    def __init__(self, events: queue.Queue):
        self.events = events

    def dispatch(self, event):
        """Put all filesystem events in a queue."""

        self.events.put(event)


def main():
    try:
        path = pathlib.Path(sys.argv[1]).absolute()
    except IndexError:
        path = pathlib.Path(os.getcwd()).absolute()
    log.warning(f"Monitoring {path}")
    log.warning("Press CTRL-C to exit (on Windows, press CTRL-BREAK)")

    event_queue = queue.Queue(maxsize=-1)
    handler = Handler(event_queue)
    observer = watchdog.observers.Observer()
    observer.schedule(handler, str(path), recursive=True)
    observer.start()

    flows_client = create_flows_client()

    try:
        timeout = None
        files = set()
        while True:
            try:
                event = event_queue.get(block=True, timeout=timeout)
            except queue.Empty:
                # .get() timed out.
                # It's now been COOL_OFF_TIME_S seconds since the last filesystem event.
                # Reset the timeout for the next batch of files and run the flow.
                timeout = None
                log.warning(f"Running the flow ({len(files)} paths were modified)")
                flows_client.run_flow(
                    flow_id=FLOW_ID,
                    flow_scope=None,
                    flow_input={
                        "count": len(files),
                    },
                    label=f"[AUTO] File system changes detected ({len(files)} paths)",
                )
                files = set()
            else:
                # .get() returned a filesystem event.
                # Make sure the next .get() call times out after COOL_OFF_TIME_S.
                timeout = COOL_OFF_TIME_S
                files.add(event.src_path)
                event_queue.task_done()
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
