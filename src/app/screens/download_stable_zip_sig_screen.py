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
download_stable_zip_sig_screen.py
"""
import os
import time
from functools import partial
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.context_instructions import Color
from src.app.screens.base_screen import BaseScreen
from src.app.screens.base_download_screen import BaseDownloadScreen
from src.utils.downloader.sig_downloader import SigDownloader


class DownloadStableZipSigScreen(BaseDownloadScreen):
    """DownloadStableZipSigScreen download the sig file for official krux zip release"""

    def __init__(self, **kwargs):
        super().__init__(
            wid="download_stable_zip_sig_screen",
            name="DownloadStableZipSigScreen",
            **kwargs,
        )
        self.to_screen = "DownloadSelfcustodyPemScreen"

        # Define some staticmethods in dynamic way
        # (so they can be called in tests)
        def on_trigger(dt):
            time.sleep(2.1)
            screen = self.manager.get_screen(self.to_screen)
            fn = partial(screen.update, name=self.name, key="public-key-certificate")
            Clock.schedule_once(fn, 0)
            self.set_screen(name=self.to_screen, direction="left")

        def on_progress(data: bytes):
            # calculate downloaded percentage
            fn = partial(
                self.update,
                name=self.name,
                key="progress",
                value={
                    "downloaded_len": self.downloader.downloaded_len,
                    "content_len": self.downloader.content_len,
                },
            )
            Clock.schedule_once(fn, 0)

        self.debug(f"Bind {self.__class__}.on_trigger={on_trigger}")
        setattr(self.__class__, "on_trigger", on_trigger)

        self.debug(f"Bind {self.__class__}.on_progress={on_progress}")
        setattr(self.__class__, "on_progress", on_progress)

        fn = partial(self.update, name=self.name, key="canvas")
        Clock.schedule_once(fn, 0)

    def update(self, *args, **kwargs):
        """Update screen with version key. Should be called before `on_enter`"""
        name = kwargs.get("name")
        key = kwargs.get("key")
        value = kwargs.get("value")

        if name in (
            "ConfigKruxInstaller",
            "DownloadStableZipSha256Screen",
            "DownloadStableZipSigScreen",
        ):
            self.debug(f"Updating {self.name} from {name}...")
        else:
            self.redirect_error(f"Invalid screen name: {name}")
            return

        if key == "locale":
            if value is not None:
                self.locale = value
            else:
                self.redirect_error(f"Invalid value for key '{key}': '{value}'")

        elif key == "canvas":
            # prepare background
            with self.canvas.before:
                Color(0, 0, 0, 1)
                Rectangle(size=(Window.width, Window.height))

        elif key == "version":
            if value is not None:
                self.version = value
                self.downloader = SigDownloader(
                    version=self.version,
                    destdir=DownloadStableZipSigScreen.get_destdir_assets(),
                )

                if self.downloader is not None:
                    url = getattr(self.downloader, "url")
                    destdir = getattr(self.downloader, "destdir")
                    downloading = self.translate("Downloading")
                    to = self.translate("to")
                    filepath = os.path.join(destdir, f"krux-{self.version}.zip.sig")

                self.ids[f"{self.id}_info"].text = "".join(
                    [
                        f"[size={self.SIZE_MP}sp]",
                        downloading,
                        "\n",
                        f"[color=#00AABB][ref={url}]{url}[/ref][/color]",
                        "\n",
                        to,
                        "\n",
                        filepath,
                        "[/size]",
                    ]
                )

            else:
                self.redirect_error(f"Invalid value for key '{key}': '{value}'")

        elif key == "progress":
            if value is not None:
                # calculate percentage of download
                lens = [value["downloaded_len"], value["content_len"]]
                percent = lens[0] / lens[1]

                of = self.translate("of")
                self.ids[f"{self.id}_progress"].text = "".join(
                    [
                        f"[size={self.SIZE_G}sp][b]{percent * 100:,.2f} %[/b][/size]",
                        "\n",
                        f"[size={self.SIZE_MP}sp]",
                        str(lens[0]),
                        f" {of} ",
                        str(lens[1]),
                        " B",
                        "[/size]",
                    ]
                )

                # When finish, change the label
                # and then change screen
                if percent == 1.00:
                    if self.downloader is not None:
                        destdir = getattr(self.downloader, "destdir")
                        downloaded = self.translate("downloaded")
                        filepath = os.path.join(destdir, f"krux-{self.version}.zip.sig")
                        self.ids[f"{self.id}_info"].text = "".join(
                            [
                                f"[size={self.SIZE_MP}sp]",
                                filepath,
                                "\n",
                                downloaded,
                                "[/size]",
                            ]
                        )

                        # When finish, change the label, wait some seconds
                        # and then change screen
                        self.trigger()

            else:
                self.redirect_error(f"Invalid value for key '{key}': '{value}'")

        else:
            self.redirect_error(f'Invalid key: "{key}"')
