# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
download_stable_zip_screen.py
"""
import math
import time
from threading import Thread
from functools import partial
from kivy.app import App
from kivy.clock import Clock
from src.app.screens.base_screen import BaseScreen
from src.app.screens.base_download_screen import BaseDownloadScreen
from src.utils.downloader.zip_downloader import ZipDownloader


class DownloadStableZipScreen(BaseDownloadScreen):
    """DownloadStableZipScreen download a official krux zip release"""

    def __init__(self, **kwargs):
        super().__init__(
            wid="download_stable_zip_screen", name="DownloadStableZipScreen", **kwargs
        )
        self.to_screen = "DownloadStableZipSha256Screen"

        # Define some staticmethods in dynamic way
        # (so they can be called in tests)
        def on_trigger(dt):
            screen = self.manager.get_screen(self.to_screen)
            fn = partial(screen.update, key="version", value=self.version)
            Clock.schedule_once(fn, 0)
            self.set_screen(name=self.to_screen, direction="left")

        def on_progress(data: bytes):
            # calculate downloaded percentage
            len1 = self.downloader.downloaded_len
            len2 = self.downloader.content_len
            p = len1 / len2

            # Format bytes (one liner)
            # https://stackoverflow.com/questions/
            # 5194057/better-way-to-convert-file-sizes-in-python#answer-52684562
            down1 = f"{len1/(1<<20):,.2f}"
            down2 = f"{len2/(1<<20):,.2f}"

            # Put all in Label widget
            self.ids[f"{self.id}_label_progress"].text = "\n".join(
                [
                    f"[size=100sp][b]{p * 100.00:.2f}%[/b][/size]",
                    f"[size=16sp]{down1} of {down2} MB[/size]",
                ]
            )

            # When finish, change the label, wait some seconds
            # and then change screen
            if p == 1.00:
                self.ids[f"{self.id}_label_info"].text = "\n".join(
                    [
                        f"{self.downloader.destdir}/krux-{self.version}.zip downloaded",
                    ]
                )
                time.sleep(2.1)  # 2.1 remember 21000000
                self.trigger()

        self.debug(f"Bind {self.__class__}.on_trigger={on_trigger}")
        setattr(self.__class__, "on_trigger", on_trigger)

        self.debug(f"Bind {self.__class__}.on_progress={on_progress}")
        setattr(self.__class__, "on_progress", on_progress)

    def update(self, *args, **kwargs):
        """Update screen with version key. Should be called before `on_enter`"""
        name = kwargs.get("name")
        key = kwargs.get("key")
        value = kwargs.get("value")

        if name in (
            "ConfigKruxInstaller",
            "MainScreen",
            "WarningAlreadyDownloadedScreen",
        ):
            self.debug(f"Updating {self.name} from {name}...")
        else:
            raise ValueError(f"Invalid screen name: {name}")

        if key == "locale":
            self.locale = value

        elif key == "version":
            self.version = value
            self.downloader = ZipDownloader(
                version=self.version,
                destdir=App.get_running_app().config.get("destdir", "assets"),
            )

            self.ids[f"{self.id}_label_info"].text = "\n".join(
                [
                    "Downloading",
                    f"[color=#00AABB][ref={self.downloader.url}]{self.downloader.url}[/ref][/color]",
                    "",
                    f"to {self.downloader.destdir}/krux-{self.version}.zip",
                ]
            )

        else:
            raise ValueError(f'Invalid key: "{key}"')
