import urllib.parse
import aiohttp
from io import BytesIO
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import urllib
from rich.console import Console


class BaseAPI:
    def __init__(self, base_url: str, debug: bool = False, console: Console = Console()):
        """
        Initialize the BaseAPI class with a base URL and optional debug mode.

        Args:
            base_url (str): The base URL of the website to interact with.
            debug (bool): Enable debug output.
        """
        self.base_url = base_url
        self.debug = debug
        self.cookies = {}
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        self.playwright = None
        self.context = None
        self.browser = None
        self.console = console

    async def  __aenter__(self):
        """Initialize Playwright, launch the browser, and fetch cookies."""
        self.playwright = await async_playwright().start()
        if self.debug: self.console.log("[white]Launching browser...[/white]")
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent=self.user_agent,
            no_viewport=True
        )

        if self.debug: self.console.log("[white]Creating page and applying Stealth mode...[/white]")
        page = await self.context.new_page()
        await stealth_async(page)

        if self.debug: self.console.log("[white]Injecting custom JavaScript for XHR requests...[/white]")
        await page.add_init_script("""
            // JavaScript to intercept and log XHR requests
            window.interceptedResponses = [];
            const originalFetch = window.fetch;
            window.fetch = async function(url, options) {
                const response = await originalFetch(url, options);
                const clone = response.clone();
                clone.text().then(data => {
                    window.interceptedResponses.push({ url, options, data });
                });
                return response;
            };
        """)

        if self.debug: self.console.log("[yellow]Navigating to base URL and fetching cookies...[/yellow]")
        response = await page.goto(self.base_url, wait_until="networkidle")
        
        if self.debug: self.console.log(f"[green]Status code: [bold cyan]{response.status}[/bold cyan], Content-Type:[/green] [bold cyan]{response.headers['content-type']}[/bold cyan]")

        self.cookies = {
            cookie["name"]: cookie["value"]
            for cookie in await self.context.cookies()
        }

        if self.debug: self.console.log(f"[green]Cookies fetched:[/green] [bold cyan]{'[/bold cyan][green], [/green][bold cyan]'.join(self.cookies.keys())}[/bold cyan]")
        self.page = page

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up Playwright resources."""
        if self.debug: self.console.log("[white]Closing browser...[/white]")
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def fetch(self, endpoint: str, method: str = "GET", body: dict = None) -> dict:
        """
        Выполнение HTTP-запроса через JavaScript в браузере.

        Args:
            endpoint (str): API endpoint.
            method (str): HTTP метод (GET/POST).
            data (dict): Данные для POST-запросов.

        Returns:
            dict: Ответ API.
        """
        url = urllib.parse.urljoin(self.base_url, endpoint)
        if self.debug: self.console.log(f"[green]Executing [bold cyan]{method}[/bold cyan] request to [bold blue]{url}[/bold blue] using JavaScript...[/green]")

        # Получение accessToken из cookies
        access_token = await self.page.evaluate("""
            () => {
                const cookies = document.cookie.split('; ').reduce((acc, cookie) => {
                    const [key, value] = cookie.split('=');
                    acc[key] = value;
                    return acc;
                }, {});
                return JSON.parse(decodeURIComponent(cookies['session'])).accessToken;
            }
        """)
        if not access_token:
            raise ValueError("Access token not found")

        # Подготовка данных
        data_str = "null" if body is None else json.dumps(body)

        # JavaScript-код для выполнения запроса
        script = f"""
            (url, method, requestData, token) => {{
                return new Promise((resolve, reject) => {{
                    const options = {{
                        method: method,
                        headers: {{
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${{token}}`
                        }},
                        body: requestData !== null ? JSON.stringify(requestData) : undefined
                    }};
                    fetch(url, options)
                        .then(response => response.json())
                        .then(data => resolve(data))
                        .catch(error => reject(error));
                }});
            }}
        """

        response = await self.page.evaluate(f"({script})(\"{url}\", \"{method}\", {data_str}, \"{access_token}\")")

        return response

    async def get_intercepted_responses(self) -> list:
        """
        Retrieve the intercepted responses logged by the injected JavaScript.

        Returns:
            list: A list of intercepted response data.
        """
        if self.debug: self.console.log("[green]Fetching intercepted responses...[/green]")
        responses = await self.page.evaluate("window.interceptedResponses")
        if self.debug: self.console.log(f"[bold green]Intercepted responses:[/bold green] [bold cyan]{responses}[/bold cyan]")
        return responses


class ImageDownloader:
    async def download_image(self, url: str) -> BytesIO:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image = BytesIO(await response.read())
                    image.name = f"{url.split('/')[-1]}"

                    return image
                else:
                    raise ValueError(f"Failed to download image, status code: {response.status}")
