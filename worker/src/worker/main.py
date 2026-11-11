import io
import logging
import os
import signal
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from PIL import Image

import worker
from worker.exceptions import ModelException
from worker.model import Predictor
from worker.utils import iso_datetime_to_date

# Load environment variables from .env file
load_dotenv()

# Read environment variables
ENDPOINT = os.environ["WORKER_ENDPOINT"]
WORKER_USER_TOKEN = os.environ["WORKER_USER_TOKEN"]

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

local_now = datetime.now().astimezone()
local_filename = local_now.strftime("%Y%m%d_%H%M%S_%z")
logs_dir = Path(worker.__file__).parent / "logs"
os.makedirs(logs_dir, exist_ok=True)
file_handler = logging.FileHandler(
    logs_dir / f"worker_{local_filename}.log", mode="a", encoding="utf-8"
)
file_handler.setLevel(logging.ERROR)

log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(log_format)
file_handler.setFormatter(log_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Set up a requests session with the authorization token
session = requests.Session()
session.headers.update(
    {
        "Authorization": f"Token {WORKER_USER_TOKEN}",
        "Accept": "application/json",
    }
)

# Initialize the Predictor instance
predictor = Predictor()


class Worker:
    def __init__(self) -> None:
        """Initialize the Worker instance."""
        self.stop_flag = threading.Event()
        self.poll_interval_seconds = 15

        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def start_worker(self) -> None:
        """Start the worker thread to poll for tasks."""
        logger.info("Worker started. Polling for tasks...")

        while not self.stop_flag.is_set():
            start_time = time.time()

            try:
                response = session.post(
                    f"{ENDPOINT}/api/wastes/captures/claim",
                    timeout=10,
                )
                response.raise_for_status()

                captures = response.json()
                menu_cache = {}
                for capture in captures:
                    try:
                        captured_at = iso_datetime_to_date(capture["captured_at"])
                        if captured_at not in menu_cache:
                            menu_day_response = session.get(
                                f"{ENDPOINT}/api/wastes/menus/{captured_at}",
                                timeout=10,
                            )
                            menu_day_response.raise_for_status()
                            menu_cache[captured_at] = menu_day_response.json()
                        dishes = menu_cache[captured_at]["dishes"] or []

                        image_url = capture["image"]
                        image_response = requests.get(image_url, timeout=5)
                        image_response.raise_for_status()
                        image = Image.open(io.BytesIO(image_response.content))
                        image.load()
                        try:
                            prediction = predictor.predict(image, dishes)
                        except ModelException as e:
                            # Model exception occurred, report failure to the server
                            try:
                                update_response = session.post(
                                    f"{ENDPOINT}/api/wastes/captures/{capture['id']}/fail",
                                    timeout=10,
                                    json={"failure_reason": str(e)},
                                )
                            except requests.exceptions.RequestException as e:
                                logger.error(
                                    f"Error reporting failure for capture {capture['id']}: {e}"
                                )
                            continue  # Skip to the next capture
                        else:
                            update_response = session.post(
                                f"{ENDPOINT}/api/wastes/predictions",
                                timeout=10,
                                json={
                                    "capture": capture["id"],
                                    "dish": prediction["dish"],
                                    "waste_bucket": prediction["waste_bucket"],
                                    "confidence": prediction["confidence"],
                                    "model_version": prediction["model_version"],
                                },
                            )
                        update_response.raise_for_status()
                    except requests.exceptions.HTTPError as http_err:
                        status_code = http_err.response.status_code  # pyright: ignore[reportOptionalMemberAccess]
                        logger.warning(
                            f"HTTP error occurred while processing capture {capture['id']}: {http_err}"
                        )
                        if status_code in (400, 404):
                            try:
                                update_response = session.post(
                                    f"{ENDPOINT}/api/wastes/captures/{capture['id']}/fail",
                                    timeout=10,
                                    json={"failure_reason": str(http_err)},
                                )
                            except requests.exceptions.RequestException as e:
                                logger.error(
                                    f"Error reporting failure for capture {capture['id']}: {e}"
                                )
                    except requests.exceptions.RequestException:
                        logger.warning(
                            "Request exception occurred while processing capture %s. Skipping this capture.",
                            capture["id"],
                        )
                    except (Image.UnidentifiedImageError, OSError) as img_err:
                        logger.error(
                            f"Image error occurred while processing capture {capture['id']}: {img_err}"
                        )
                        try:
                            update_response = session.post(
                                f"{ENDPOINT}/api/wastes/captures/{capture['id']}/fail",
                                timeout=10,
                                json={"failure_reason": str(img_err)},
                            )
                        except requests.exceptions.RequestException as e:
                            logger.error(
                                f"Error reporting failure for capture {capture['id']}: {e}"
                            )
                    except Exception:
                        logger.exception(
                            "Unexpected error occurred while processing capture %s. Skipping this capture.",
                            capture.get("id") if isinstance(capture, dict) else capture,
                        )
            except requests.exceptions.RequestException as e:
                logger.error("Error fetching tasks: %s", e)
                captures = []
            except Exception:
                logger.exception("Unexpected error occurred while polling for tasks.")
                captures = []
            else:
                logger.info(
                    "Polled for tasks. Found %d pending tasks.",
                    len(captures),
                )

            elapsed = time.time() - start_time
            sleep_needed = max(0, self.poll_interval_seconds - elapsed)

            logger.info(
                "Finish polling for tasks. Time taken: %.2f seconds. Sleeping for %.2f seconds.",
                elapsed,
                sleep_needed,
            )

            # Only sleep if there are no captures to process, otherwise continue immediately to process the next batch.
            if len(captures) == 0:
                logger.info(
                    "No captures to process. Sleeping for %.2f seconds.",
                    sleep_needed,
                )
                self.stop_flag.wait(sleep_needed)

    def exit_gracefully(self, signum: int, frame: Any) -> None:
        """Set the stop flag to exit the worker gracefully."""
        self.stop_flag.set()
        logger.info("Worker is exiting gracefully.")


if __name__ == "__main__":
    worker_obj = Worker()
    worker_obj.start_worker()
