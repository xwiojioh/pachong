from contextlib import suppress

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


class BrowserRenderer:
    def __init__(self, logger=None):
        self.logger = logger or (lambda *_args, **_kwargs: None)

    def render(self, url, request_config):
        timeout_seconds = int(request_config.get('timeout') or 30)
        timeout_ms = timeout_seconds * 1000
        wait_for_timeout_ms = int(request_config.get('wait_for_timeout_ms') or 3000)
        wait_for_selector = (request_config.get('wait_for_selector') or '').strip()
        wait_until = request_config.get('wait_until') or 'domcontentloaded'
        emulate_mobile = bool(request_config.get('emulate_mobile'))
        device_name = request_config.get('device_name') or ('iPhone 13' if emulate_mobile else '')
        headers = request_config.get('headers') or {}
        cookies = request_config.get('cookies') or {}

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context_kwargs = {}

            if device_name and device_name in playwright.devices:
                context_kwargs.update(playwright.devices[device_name])
            elif emulate_mobile:
                context_kwargs.update(
                    {
                        'viewport': {'width': 390, 'height': 844},
                        'is_mobile': True,
                        'has_touch': True,
                    }
                )

            if headers:
                context_kwargs['extra_http_headers'] = headers

            context = browser.new_context(**context_kwargs)
            try:
                if cookies:
                    context.add_cookies(
                        [
                            {
                                'name': key,
                                'value': str(value),
                                'url': url,
                                'path': '/',
                            }
                            for key, value in cookies.items()
                            if value not in (None, '')
                        ]
                    )

                page = context.new_page()
                page.goto(url, wait_until=wait_until, timeout=timeout_ms)

                if wait_for_selector:
                    page.wait_for_selector(wait_for_selector, timeout=timeout_ms)

                if wait_for_timeout_ms > 0:
                    page.wait_for_timeout(wait_for_timeout_ms)

                return {
                    'html': page.content(),
                    'title': page.title(),
                    'final_url': page.url,
                }
            except PlaywrightTimeoutError as error:
                raise RuntimeError(f'动态渲染超时: {error}') from error
            finally:
                with suppress(Exception):
                    context.close()
                with suppress(Exception):
                    browser.close()
