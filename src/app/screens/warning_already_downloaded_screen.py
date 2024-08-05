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
about_screen.py
"""
from functools import partial
from kivy.clock import Clock
from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.context_instructions import Color
from kivy.core.window import Window
from kivy.weakproxy import WeakProxy
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from src.utils.constants import get_name, get_version
from src.app.screens.base_screen import BaseScreen
from src.i18n import T


class WarningAlreadyDownloadedScreen(BaseScreen):
    """WarningAlreadyDownloadedScreen warns user about an asset that is already downloaded"""

    def __init__(self, **kwargs):
        super().__init__(
            wid="warning_already_downloaded_screen",
            name="WarningAlreadyDownloadedScreen",
            **kwargs,
        )

        self.make_grid(wid=f"{self.id}_grid", rows=2)

        warning = Label(
            text="",
            markup=True,
            valign="center",
            halign="center",
        )
        warning.id = f"{self.id}_label"
        self.ids[f"{self.id}_grid"].add_widget(warning)
        self.ids[warning.id] = WeakProxy(warning)

        stack = StackLayout()
        stack.id = f"{self.id}_stack_buttons"
        self.ids[f"{self.id}_grid"].add_widget(stack)
        self.ids[stack.id] = WeakProxy(stack)

        buttons = [f"{self.id}_download_button", f"{self.id}_proceed_button"]

        for wid in buttons:

            def _press(instance):
                self.debug(f"Calling Button::{instance.id}::on_press")
                self.set_background(wid=instance.id, rgba=(0.25, 0.25, 0.25, 1))

            def _release(instance):
                self.debug(f"Calling Button::{instance.id}::on_release")
                self.set_background(wid=instance.id, rgba=(0, 0, 0, 1))

                if instance.id == f"{self.id}_download_button":
                    main_screen = self.manager.get_screen("MainScreen")
                    download_screen = self.manager.get_screen("DownloadStableZipScreen")
                    fn = partial(
                        download_screen.update,
                        name=self.name,
                        key="version",
                        value=main_screen.version,
                    )
                    Clock.schedule_once(fn, 0)
                    self.set_screen(name="DownloadStableZipScreen", direction="right")

                if instance.id == f"{self.id}_proceed_button":
                    self.set_screen(name="VerifyStableZipScreen", direction="right")

            self.make_stack_button(
                root_widget=f"{self.id}_stack_buttons",
                wid=wid,
                size_hint=(0.5, None),
                on_press=_press,
                on_release=_release,
            )

        fn = partial(self.update, name=self.name, key="canvas")
        Clock.schedule_once(fn, 0)

    def update(self, *args, **kwargs):
        """Update buttons on related screen"""
        name = kwargs.get("name")
        key = kwargs.get("key")
        value = kwargs.get("value")

        if name in (
            "ConfigKruxInstaller",
            "MainScreen",
            "WarningAlreadyDownloadedScreen",
        ):
            self.debug(f"Updating {self.name} from {name}")
        else:
            raise ValueError(f"Invalid screen name: {name}")

        # Check locale
        if key == "locale":
            self.locale = value

        elif key == "canvas":
            # prepare background
            with self.canvas.before:
                Color(0, 0, 0, 1)
                Rectangle(size=(Window.width, Window.height))

        elif key == "version":
            warning_msg = self.translate("Assets already downloaded")
            ask_proceed = self.translate(
                "Do you want to proceed with the same file or do you want to download it again?"
            )
            download_msg = self.translate("Download again")
            proceed_msg = self.translate("Proceed with files")

            self.ids[f"{self.id}_download_button"].text = (
                f"[color=#00ff00]{download_msg}[/color]"
            )
            self.ids[f"{self.id}_proceed_button"].text = (
                f"[color=#00ccef]{proceed_msg}[/color]"
            )
            self.ids[f"{self.id}_label"].text = "\n".join(
                [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    f"[size=36sp][color=#efcc00][b]{warning_msg}[/b][/color][/size]",
                    "",
                    "",
                    "",
                    f"[size=20sp][color=#efcc00]krux-{value}.zip[/color][/size]",
                    "",
                    f"[size=20sp][color=#efcc00]krux-{value}.zip.sha256.txt[/color][/size]",
                    "",
                    f"[size=20sp][color=#efcc00]krux-{value}.zip.sig[/color][/size]",
                    "",
                    "[size=20sp][color=#efcc00]selfcustody.pem[/color][/size]",
                    "",
                    "",
                    "",
                    f"[size=16sp]{ask_proceed}[/size]",
                    "",
                    "",
                    "",
                ]
            )

        else:
            raise ValueError(f'Invalid key: "{key}"')
