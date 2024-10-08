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
import webbrowser
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.context_instructions import Color
from src.utils.constants import get_name, get_version
from src.app.screens.base_screen import BaseScreen


class AboutScreen(BaseScreen):
    """Flash screen is where flash occurs"""

    def __init__(self, **kwargs):
        super().__init__(wid="about_screen", name="AboutScreen", **kwargs)
        self.src_code = (
            "https://selfcustody.github.io/krux/getting-started/installing/from-gui/"
        )

        self.make_grid(wid="about_screen_grid", rows=1)

        self.make_label(
            wid=f"{self.id}_label",
            text="",
            root_widget=f"{self.id}_grid",
            markup=True,
            halign="justify",
        )

        def _on_ref_press(*args):
            self.debug(f"Calling Button::{args[0]}::on_ref_press")
            self.debug(f"Opening {args[1]}")

            if args[1] == "Back":
                self.set_screen(name="MainScreen", direction="right")

            elif args[1] == "X":
                webbrowser.open("https://x.com/selfcustodykrux")

            elif args[1] == "SourceCode":
                webbrowser.open(self.src_code)

            else:
                self.redirect_error(f"Invalid ref: {args[1]}")

        setattr(self, f"on_ref_press_{self.id}_label", _on_ref_press)
        self.ids[f"{self.id}_label"].bind(on_ref_press=_on_ref_press)

        fns = [
            partial(self.update, name=self.name, key="canvas"),
            partial(self.update, name=self.name, key="locale", value=self.locale),
        ]

        for fn in fns:
            Clock.schedule_once(fn, 0)

    def update(self, *args, **kwargs):
        """Update buttons from selected device/versions on related screens"""
        name = kwargs.get("name")
        key = kwargs.get("key")
        value = kwargs.get("value")

        # Check if update to screen
        if name in ("KruxInstallerApp", "ConfigKruxInstaller", "AboutScreen"):
            self.debug(f"Updating {self.name} from {name}...")
        else:
            self.redirect_error(msg=f"Invalid screen name: {name}")

        if key == "canvas":
            # prepare background
            with self.canvas.before:
                Color(0, 0, 0, 1)
                Rectangle(size=(Window.width, Window.height))

        # Check locale
        elif key == "locale":
            if value is not None:
                self.locale = value
                follow = self.translate("follow us on X")
                back = self.translate("Back")

                self.ids[f"{self.id}_label"].text = "".join(
                    [
                        f"[size={self.SIZE_G}sp]",
                        f"[ref=SourceCode][b]v{get_version()}[/b][/ref]",
                        "[/size]",
                        "\n",
                        "\n" f"[size={self.SIZE_M}sp]",
                        f"{follow}: ",
                        "[color=#00AABB]",
                        "[ref=X][u]@selfcustodykrux[/u][/ref]",
                        "[/color]",
                        "[/size]",
                        "\n",
                        "\n",
                        f"[size={self.SIZE_M}sp]",
                        "[color=#00FF00]",
                        "[ref=Back]",
                        f"[u]{back}[/u]",
                        "[/ref]",
                        "[/color]",
                        "[/size]",
                    ]
                )

            else:
                self.redirect_error(f"Invalid value for key '{key}': '{value}'")

        else:
            self.redirect_error(msg=f'Invalid key: "{key}"')
