from loguru import logger


class Twitter:
    def __init__(self, page) -> None:
        self.page = page

    def _generate_script(self, auth_token):
        script = f"""
        function setCookie(name, value, options = {{}}) {{
            options = {{ path: "/", ...options }};
            if (options.expires instanceof Date) {{
                options.expires = options.expires.toUTCString();
            }}
            let updatedCookie =
                encodeURIComponent(name) + "=" + encodeURIComponent(value);
            for (let optionKey in options) {{
                updatedCookie += "; " + optionKey;
                let optionValue = options[optionKey];
                if (optionValue !== true) {{
                    updatedCookie += "=" + optionValue;
                }}
            }}
            document.cookie = updatedCookie;
        }}

        function deleteAllCookies() {{
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {{
                const cookie = cookies[i];
                const eqPos = cookie.indexOf("=");
                const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
                document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
            }}
        }}

        deleteAllCookies();

        setCookie("auth_token", "{auth_token}", {{
            secure: true,
            "max-age": 3600 * 24 * 365,
            domain: "twitter.com",
        }});

        setTimeout(() => {{
            window.location.href = "https://twitter.com";
        }}, 2500);
    """
        return script

    def login_by_token(self, token):
        url = "https://twitter.com/i/flow/login"
        self.page.get(url)

        if not token:
            logger.warning("token参数传入为空")
            return

        # token login
        script = self._generate_script(token)
        self.page.run_js(script, as_expr=True)
        logger.info(f"Login twitter for token: {token}")

    def login_by_user(self, username, passwd):
        self.page.get("https://twitter.com/i/flow/login")
        self.page.ele("@autocomplete=username").input(username)
        next_button = (self.page.eles("@@role=button@@tabindex=0"))[2]
        next_button.click()
        self.page.ele("@autocomplete=current-password").input(passwd)
        login_button = (self.page.eles("@@role=button@@tabindex=0"))[3]
        login_button.click()

    def get_token(self):
        self.page.get("https://twitter.com/")
        self.page.set.window.max()
        for i in self.page.get_cookies(as_dict=False, all_domains=True):
            name = i.get("name")
            if name == "auth_token":
                return i.get("value")

    def get_last_post_url(self):
        last_tab = self.page.get_tab(0)
        url = last_tab.url
        if "twitter" not in url:
            logger.warning("不在推特url...")
            return

        last_tab.ele("@aria-label=Profile").click()
        ele = last_tab.ele("x://div[@data-testid='User-Name']/div[2]/div/div[3]/a")
        herf = ele.link

        return herf
