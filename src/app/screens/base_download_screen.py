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
base_download_screen.py
"""
import typing
from functools import partial
from threading import Thread
from kivy.clock import Clock, ClockEvent
from kivy.weakproxy import WeakProxy
from kivy.uix.label import Label
from src.app.screens.base_screen import BaseScreen
from src.utils.downloader.asset_downloader import AssetDownloader


class BaseDownloadScreen(BaseScreen):
    """BaseDownloadScreen setup some initial variables for usable Downloader screens"""

    def __init__(self, wid: str, name: str, **kwargs):
        super().__init__(wid=wid, name=name, **kwargs)
        self.make_grid(wid=f"{self.id}_grid", rows=2)

        self._downloader = None
        self._thread = None
        self._trigger = None
        self.version = None
        self._to_screen = ""

        # progress label, show a "Connecting"
        # before start the download to make
        connecting = self.translate("Connecting")
        text = "".join(
            [
                f"[size={self.SIZE_G}]",
                f"{connecting}...",
                "[/size]",
                "[color=#efcc00]",
                "[/color]",
            ]
        )

        progress = Label(
            text=text,
            markup=True,
            valign="center",
            halign="center",
        )

        # information label
        # it has data about url
        # and downloaded paths
        asset_label = Label(markup=True, valign="center", halign="center")

        # setup progress label
        progress.id = f"{self.id}_progress"
        self.ids[f"{self.id}_grid"].add_widget(progress)
        self.ids[progress.id] = WeakProxy(progress)

        # setup information label
        asset_label.id = f"{self.id}_info"
        self.ids[f"{self.id}_grid"].add_widget(asset_label)
        self.ids[asset_label.id] = WeakProxy(asset_label)

    @property
    def to_screen(self) -> str:
        self.debug(f"getter::to_screen={self._to_screen}")
        return self._to_screen

    @to_screen.setter
    def to_screen(self, value: str):
        self.debug(f"setter::to_screen={value}")
        self._to_screen = value

    @property
    def downloader(self) -> AssetDownloader | None:
        """Get an `AssetDownloader`"""
        self.debug(f"getter::downloader={self._downloader}")
        return self._downloader

    @downloader.setter
    def downloader(self, value: AssetDownloader):
        """Set an `AssetDownloader`"""
        self.debug(f"setter::downloader={value}")
        self._downloader = value

    @downloader.deleter
    def downloader(self):
        """Delete an `AssetDownloader`"""
        self.debug(f"deleter::downloader={self._downloader}")
        del self._downloader

    @property
    def thread(self) -> Thread | None:
        self.debug(f"getter::thread={self._thread}")
        return self._thread

    @thread.setter
    def thread(self, value: Thread):
        """
        Wait until download thread finish,
        when finished call this callback

        See https://kivy.org/doc/stable/guide/events.html
        """
        self.debug(f"setter::thread={self._thread}->{value}")
        self._thread = value

    @property
    def trigger(self) -> ClockEvent:
        """Trigger is a `ClockEvent` that should be triggered after download is done"""
        self.debug(f"getter::trigger={self._trigger}")
        return self._trigger

    @trigger.setter
    def trigger(self, value: typing.Callable):
        """Create a `ClockEvent` given a callback"""
        self.debug(f"getter::trigger={value}")
        self._trigger = Clock.create_trigger(value)

    @trigger.deleter
    def trigger(self):
        """Delete a `ClockEvent`"""
        self.debug(f"deleter::trigger={self._trigger}")
        del self._trigger

    def on_enter(self):
        """
        Event fired when the screen is displayed and the entering animation is complete.

        Every inherithed class should implement it own `on_trigger` and `on_progress`
        staticmethods. The method `on_progress` should call `self.trigger` ath the end:
        """
        if self.downloader is not None:
            # on trigger should be defined on inherited classes
            self.trigger = getattr(self.__class__, "on_trigger")

            # on progress should be defined on inherited classes
            on_progress = getattr(self.__class__, "on_progress")
            _fn = partial(self.downloader.download, on_data=on_progress)

            # Now run it as a partial function
            # on parallel thread to not block
            # the process during the kivy cycles
            self.thread = Thread(name=self.name, target=_fn)
            self.thread.start()
        else:
            self.redirect_error("Downloader isnt configured. Use `update` method first")
