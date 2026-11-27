import time
from typing import Any, Callable, Optional

from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.logger import setup_logger
from utils.helper import highlight_element,take_screenshot


class BasePage:
    def __init__(self, page: Page, default_timeout: int = 15000):
        self.page = page
        self.logger = setup_logger(self.__class__.__name__)
        self.default_timeout = default_timeout  # milliseconds, per attempt
        self.page.set_default_timeout(default_timeout)

    # ---------- Retry ----------
    def perform_with_retry(
        self,
        action: Callable[[], Any],
        description: str,
        retries: int = 3,
        delay: float = 1,
    ) -> Any:
        for attempt in range(1, retries + 1):
            try:
                return action()
            except PlaywrightTimeoutError:
                self.logger.warning(f"{description} failed (attempt {attempt}/{retries})")
                if attempt == retries:
                    self.logger.error(f"{description} failed after {retries} attempts")
                    raise  # re-raise the original error
                time.sleep(delay)

    def _locator(self, selector: str):
        return self.page.locator(selector)

    # ---------- Waits ----------
    def wait_for_visible(self, selector: str, timeout: Optional[int] = None) -> None:
        self.logger.info(f"Waiting for {selector} to be visible")
        self._locator(selector).wait_for(state="visible", timeout=timeout or self.default_timeout)

    def wait_for_attached(self, selector: str, timeout: Optional[int] = None) -> None:
        self.logger.info(f"Waiting for {selector} to be attached")
        self._locator(selector).wait_for(state="attached", timeout=timeout or self.default_timeout)

    def wait_for_hidden(self, selector: str, timeout: Optional[int] = None) -> None:
        self.logger.info(f"Waiting for {selector} to be hidden")
        self._locator(selector).wait_for(state="hidden", timeout=timeout or self.default_timeout)

    def wait_for_enabled(self, selector: str, timeout: Optional[int] = None) -> None:
        self.logger.info(f"Waiting for {selector} to be enabled")
        expect(self._locator(selector)).to_be_enabled(timeout=timeout or self.default_timeout)

    # ---------- Element Actions ----------
    def click(self, selector: str) -> None:
        def action():
            highlight_element(self.page, selector)
            self.logger.info(f"Clicking {selector}")
            self._locator(selector).click()

        self.perform_with_retry(action, f"Click {selector}")

    def double_click(self, selector: str) -> None:
        def action():
            highlight_element(self.page, selector)
            self.logger.info(f"Double-clicking {selector}")
            self._locator(selector).dblclick()

        self.perform_with_retry(action, f"Double click {selector}")

    def enter_text(self, selector: str, text: str, mask: bool = False) -> None:
        """fill() already clears the field. Use mask=True for passwords."""
        def action():
            highlight_element(self.page, selector)
            shown = "*" * len(text) if mask else text
            self.logger.info(f"Entering '{shown}' in {selector}")
            self._locator(selector).fill(text)

        self.perform_with_retry(action, f"Enter text into {selector}")

    def append_text(self, selector: str, text: str, delay_ms: int = 0) -> None:
        def action():
            highlight_element(self.page, selector)
            self.logger.info(f"Appending '{text}' to {selector}")
            self._locator(selector).press_sequentially(text, delay=delay_ms)

        self.perform_with_retry(action, f"Append text into {selector}")

    def select_dropdown(self, selector: str, option_text: str) -> None:
        def action():
            highlight_element(self.page, selector)
            self.logger.info(f"Selecting '{option_text}' in {selector}")
            self._locator(selector).select_option(label=option_text)

        self.perform_with_retry(action, f"Select dropdown {selector}")

    def get_text(self, selector: str) -> str:
        def action():
            text = self._locator(selector).inner_text()
            self.logger.info(f"Text from {selector}: '{text}'")
            return text

        return self.perform_with_retry(action, f"Get text from {selector}")

    def get_attribute(self, selector: str, attribute_name: str) -> Optional[str]:
        def action():
            value = self._locator(selector).get_attribute(attribute_name)
            self.logger.info(f"Attribute '{attribute_name}' of {selector}: '{value}'")
            return value

        return self.perform_with_retry(action, f"Get attribute '{attribute_name}' from {selector}")

    # ---------- State checks (instant, no retry) ----------
    def is_visible(self, selector: str) -> bool:
        visible = self._locator(selector).is_visible()
        self.logger.info(f"Visibility of {selector}: {visible}")
        return visible

    def is_enabled(self, selector: str) -> bool:
        enabled = self._locator(selector).is_enabled()
        self.logger.info(f"Enabled state of {selector}: {enabled}")
        return enabled

    def is_checked(self, selector: str) -> bool:
        checked = self._locator(selector).is_checked()
        self.logger.info(f"Checked state of {selector}: {checked}")
        return checked

    # ---------- User-Like Actions ----------
    def hover(self, selector: str) -> None:
        def action():
            highlight_element(self.page, selector)
            self.logger.info(f"Hovering over {selector}")
            self._locator(selector).hover()

        self.perform_with_retry(action, f"Hover over {selector}")

    def scroll_into_view(self, selector: str) -> None:
        def action():
            self.logger.info(f"Scrolling to {selector}")
            self._locator(selector).scroll_into_view_if_needed()

        self.perform_with_retry(action, f"Scroll to {selector}")

    def take_element_screenshot(self, selector: str, path: str) -> None:
        def action():
            self.logger.info(f"Taking screenshot of {selector}")
            self._locator(selector).screenshot(path=path)

        self.perform_with_retry(action, f"Screenshot {selector}")

    # ---------- Assertions (use expect: it retries automatically) ----------
    def assert_text(self, selector: str, expected_text: str) -> None:
        self.logger.info(f"Asserting text of {selector} == '{expected_text}'")
        expect(self._locator(selector)).to_have_text(expected_text, timeout=self.default_timeout)

    def assert_element_visible(self, selector: str) -> None:
        self.logger.info(f"Asserting {selector} is visible")
        expect(self._locator(selector)).to_be_visible(timeout=self.default_timeout)

    def assert_element_not_visible(self, selector: str) -> None:
        self.logger.info(f"Asserting {selector} is not visible")
        expect(self._locator(selector)).to_be_hidden(timeout=self.default_timeout)

    # ---------- Utility ----------
    def go_to(self, url: str) -> None:
        def action():
            self.logger.info(f"Navigating to: {url}")
            self.page.goto(url, wait_until="load")

        self.perform_with_retry(action, f"Navigate to {url}")

    def reload_page(self) -> None:
        def action():
            self.logger.info("Reloading page")
            self.page.reload(wait_until="load")

        self.perform_with_retry(action, "Reload page")

    def execute_script(self, script: str) -> Any:
        self.logger.info("Executing JavaScript")
        return self.page.evaluate(script)

    def get_current_url(self) -> str:
        url = self.page.url
        self.logger.info(f"Current URL: '{url}'")
        return url