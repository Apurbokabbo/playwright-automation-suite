import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config.base_config import BaseConfig
from utils.logger import setup_logger

log = setup_logger(__name__)


def _safe_name(name: str) -> str:
    """Make a string safe to use as a file name."""
    return re.sub(r"[^\w\-.]+", "_", name).strip("_") or "screenshot"


def take_screenshot(page: Page, name: str, full_page: bool = True) -> Optional[Path]:
    """Save a screenshot and return its path, or None if it failed."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder = Path(BaseConfig.SCREEN_SHOT_DIR)
        folder.mkdir(parents=True, exist_ok=True)
        file_path = folder / f"{_safe_name(name)}_{timestamp}.png"

        # Non-fatal: some pages never reach networkidle
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except PlaywrightTimeoutError:
            log.warning("Page did not reach networkidle, taking screenshot anyway")

        page.screenshot(path=str(file_path), full_page=full_page, timeout=60000)
        log.info("Screenshot saved: %s", file_path)
        return file_path

    except Exception:
        log.exception("Failed to take screenshot '%s'", name)
        return None


def highlight_element(page: Page, selector: str, color: str = "red", duration: Optional[float] = 0.5) -> None:
    """Outline an element. If duration is None, the highlight stays until the page reloads."""
    try:
        page.locator(selector).first.evaluate(
            """(el, [color, ms]) => {
                const original = el.style.outline;
                el.style.outline = `3px solid ${color}`;
                if (ms !== null) {
                    setTimeout(() => { el.style.outline = original; }, ms);
                }
            }""",
            [color, None if duration is None else int(duration * 1000)],
        )
    except Exception:
        log.exception("Failed to highlight element '%s'", selector)


def screenshot_with_highlight(page: Page, selector: str, name: str, color: str = "red") -> Optional[Path]:
    """Highlight an element, then take a screenshot that includes the highlight."""
    highlight_element(page, selector, color=color, duration=None)
    return take_screenshot(page, name)