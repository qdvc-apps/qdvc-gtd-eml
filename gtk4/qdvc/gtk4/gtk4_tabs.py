"""Tabs: emails opened in their own tab beside the viewer (the macOS
edition's message windows, as GNOME tabs).

The main window's content is an Adw.TabView whose first page, pinned, is the
viewer (sidebar, list, reading pane). "Open in New Tab" adds a MessageTab: the
reading pane for one email, followed by file name so it survives moves. The
tab bar hides itself while the viewer is the only tab.

A message tab dragged out of the tab bar becomes a MessageWindow: a window
with its own tab view, holding message tabs only (the viewer can't be
dragged out: it is pinned). Message windows have no actions of their own:
their "win." actions are the main window's, which act on the email of the tab
shown in whichever window is active (MainWindow.current_tab). Tabs can be
dragged back into the main window.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk  # noqa: E402

from .. import APP_NAME  # noqa: E402
from .gtk4_reading_pane import ReadingPane  # noqa: E402
from .gtk4_widgets import vbox  # noqa: E402

# Ctrl+Tab and Ctrl+Page Up/Down switch tabs, as in GNOME's other tabbed
# apps. Alt+1…9 are the window's own select-tab actions (so they also work in
# message windows), and Ctrl+Home/End are left to lists and text fields.
TAB_SHORTCUTS = (Adw.TabViewShortcuts.CONTROL_TAB | Adw.TabViewShortcuts.CONTROL_SHIFT_TAB |
                 Adw.TabViewShortcuts.CONTROL_PAGE_UP | Adw.TabViewShortcuts.CONTROL_PAGE_DOWN)
MESSAGE_ICON = "mail-unread-symbolic"


def make_tab_area(owner):
    """(box, tab_view, tab_bar): a tab bar (hidden with one tab, and a handle
    for moving the window, since it sits above the panes' header bars) over
    a tab view whose pages `owner` (the main window) looks after."""
    view = Adw.TabView(vexpand=True)
    view.set_shortcuts(TAB_SHORTCUTS)
    # Not `autohide`: it never hides a bar with a pinned tab, and the viewer
    # is one. Shown with two tabs or more, and while a tab is being dragged
    # (so a tab can be dropped back in).
    bar = Adw.TabBar(view=view, autohide=False)
    handle = Gtk.WindowHandle(child=bar, visible=False)

    def update(*_):
        handle.set_visible(view.get_n_pages() > 1 or view.get_is_transferring_page())
    view.connect("notify::n-pages", update)
    view.connect("notify::is-transferring-page", update)
    box = vbox()
    box.append(handle)
    box.append(view)
    view.connect("close-page", owner.on_close_page)
    view.connect("create-window", lambda _v: MessageWindow(owner).tab_view)
    view.connect("notify::selected-page", lambda *_: owner.tab_context_changed())
    view.connect("page-attached", lambda *_: owner.tab_context_changed())
    return box, view, bar


class MessageTab(Adw.Bin):
    """One email in a tab, by file name."""

    def __init__(self, window, filename):
        super().__init__()
        self.window = window
        self.filename = filename
        self.page = None
        self.pane = ReadingPane(window, in_tab=True, on_open_history=self._open_history)
        self.set_child(self.pane)

    def record(self):
        return self.window.record_by_name(self.filename)

    def refresh(self):
        """Show the email as it is now (after a reload), or say it has gone."""
        r = self.record()
        if r is None:
            self.pane.show_gone(self.filename)
            title = self.filename
        else:
            self.pane.show_record(r, self.window.reading_context(r))
            title = r.subject
        if self.page is not None:
            self.page.set_title(title)
            self.page.set_tooltip(f"{title}\n{self.filename}")

    def show_filename(self, filename):
        """A history link clicked in this tab shows that email here."""
        self.filename = filename
        self.refresh()
        self.window.tab_context_changed()

    def _open_history(self, record):
        self.show_filename(record.filename)


class MessageWindow(Adw.ApplicationWindow):
    """A window for message tabs dragged out of the main window."""

    def __init__(self, main):
        super().__init__(application=main.get_application(), title=APP_NAME)
        self.main_window = main
        self.set_icon_name(main.icon_name)
        self.set_default_size(760, 820)
        self.set_size_request(360, 294)
        # Every "win." action here is the main window's (see the module doc).
        self.insert_action_group("win", main)
        box, self.tab_view, self.tab_bar = make_tab_area(main)
        self.toasts = Adw.ToastOverlay(child=box)
        self.set_content(self.toasts)
        self.tab_view.connect("notify::n-pages", self._on_n_pages)
        self.connect("notify::is-active", lambda *_: main.host_activated(self))
        self.connect("close-request", self._on_close_request)
        main.message_windows.append(self)
        GLib.idle_add(lambda: (self.present(), False)[1])

    def _on_n_pages(self, *_):
        if self.tab_view.get_n_pages() == 0:
            # The last tab was closed or dragged elsewhere.
            GLib.idle_add(lambda: (self.close(), False)[1])

    def _on_close_request(self, *_):
        main = self.main_window
        for page in list(_pages(self.tab_view)):
            main.remember_closed(page)
        if self in main.message_windows:
            main.message_windows.remove(self)
        main.host_activated(main)
        return False


def _pages(view):
    return [view.get_nth_page(i) for i in range(view.get_n_pages())]


def pages(view):
    return _pages(view)


def themed(icon):
    return Gio.ThemedIcon.new(icon)
