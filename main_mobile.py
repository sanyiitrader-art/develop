import os
import threading
import shutil

try:
    from core.analyser import analyse_chart
    from core.drawer import draw_levels
    from core.history import save_analysis, load_history
    from config import ANALYZED_IMAGE_PATH, LIVE_CHART_PATH
except Exception as e:
    print(f"Import error: {e}")
    ANALYZED_IMAGE_PATH = "analyzed_chart.png"
    LIVE_CHART_PATH = "live_chart.png"
    def analyse_chart(p): return None
    def draw_levels(a): pass
    def save_analysis(a, p): pass
    def load_history(): return []

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

# Colors
GOLD = get_color_from_hex("#f59e0b")
GREEN = get_color_from_hex("#10b981")
RED = get_color_from_hex("#ef4444")
BLUE = get_color_from_hex("#3b82f6")
BG_DARK = get_color_from_hex("#0a0c0f")
BG2 = get_color_from_hex("#111318")
BG3 = get_color_from_hex("#0d1117")
WHITE = get_color_from_hex("#e2e8f0")
GRAY = get_color_from_hex("#4a5568")

Window.clearcolor = get_color_from_hex("#0a0c0f")


def make_button(text, bg_color, text_color, callback, height=50):
    btn = Button(
        text=text,
        size_hint=(1, None),
        height=dp(height),
        background_normal='',
        background_color=bg_color,
        color=text_color,
        font_size=dp(14),
        bold=True
    )
    btn.bind(on_press=callback)
    return btn


def make_label(text, color=None, size=14, bold=False, align='left'):
    if color is None:
        color = WHITE
    lbl = Label(
        text=text,
        color=color,
        font_size=dp(size),
        bold=bold,
        halign=align,
        valign='middle',
        size_hint_y=None,
    )
    lbl.bind(texture_size=lambda instance, value: setattr(
        instance, 'height', value[1] + dp(8)))
    lbl.bind(width=lambda instance, value: setattr(
        instance, 'text_size', (value, None)))
    return lbl


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_analysis = None
        self.build_ui()

    def build_ui(self):
        scroll = ScrollView()
        main = BoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None
        )
        main.bind(minimum_height=main.setter('height'))

        # Header
        header = BoxLayout(
            size_hint=(1, None),
            height=dp(60),
            padding=dp(8)
        )
        with header.canvas.before:
            Color(*BG2)
            self.header_rect = Rectangle(
                pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(self.header_rect, 'pos', v))
        header.bind(size=lambda i, v: setattr(self.header_rect, 'size', v))
        header.add_widget(make_label(
            "CHARTMIND AI", color=GOLD, size=16, bold=True))
        header.add_widget(make_label(
            "AI Ready", color=GREEN, size=12, align='right'))
        main.add_widget(header)

        # Status
        self.status_label = make_label(
            "Upload a chart to begin",
            color=GRAY, size=12, align='center')
        main.add_widget(self.status_label)

        # Chart image
        self.chart_image = Image(
            source='',
            size_hint=(1, None),
            height=dp(200),
            allow_stretch=True,
            keep_ratio=True
        )
        main.add_widget(self.chart_image)

        # Upload button
        upload_btn = make_button(
            "Upload Chart",
            bg_color=get_color_from_hex("#1a1500"),
            text_color=GOLD,
            callback=self.open_file_picker,
            height=52
        )
        main.add_widget(upload_btn)

        # Options
        self.options_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(0)
        )
        options_title = make_label(
            "How do you want to see the result?",
            color=GRAY, size=12, align='center')
        btn_image = make_button(
            "By Image",
            bg_color=get_color_from_hex("#1a2a1a"),
            text_color=GREEN,
            callback=self.show_image_result
        )
        btn_desc = make_button(
            "By Description",
            bg_color=get_color_from_hex("#111a2e"),
            text_color=BLUE,
            callback=self.show_description
        )
        btn_signal = make_button(
            "Buy or Sell",
            bg_color=get_color_from_hex("#1a1500"),
            text_color=GOLD,
            callback=self.show_direction
        )
        self.options_layout.add_widget(options_title)
        self.options_layout.add_widget(btn_image)
        self.options_layout.add_widget(btn_desc)
        self.options_layout.add_widget(btn_signal)
        main.add_widget(self.options_layout)

        # Result area
        self.result_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(0)
        )
        main.add_widget(self.result_layout)

        # History
        main.add_widget(make_label(
            "RECENT HISTORY",
            color=GRAY, size=9, bold=True))
        self.history_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            size_hint=(1, None),
            height=dp(0)
        )
        main.add_widget(self.history_layout)

        scroll.add_widget(main)
        self.add_widget(scroll)
        self.load_history()

    def open_file_picker(self, instance):
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=dp(8)
        )

        # Try phone storage paths
        start_path = '/sdcard'
        if not os.path.exists(start_path):
            start_path = os.path.expanduser('~')

        chooser = FileChooserIconView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.webp'],
            path=start_path
        )
        content.add_widget(chooser)

        btn_row = BoxLayout(
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(8)
        )
        select_btn = Button(
            text='Select',
            background_normal='',
            background_color=GOLD,
            color=get_color_from_hex("#000000"),
            bold=True
        )
        cancel_btn = Button(
            text='Cancel',
            background_normal='',
            background_color=get_color_from_hex("#1e2330"),
            color=WHITE
        )
        btn_row.add_widget(select_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title='Select Chart Image',
            content=content,
            size_hint=(0.95, 0.85),
            title_color=GOLD
        )

        def on_select(inst):
            if chooser.selection:
                popup.dismiss()
                self.load_image(chooser.selection[0])

        def on_cancel(inst):
            popup.dismiss()

        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=on_cancel)
        popup.open()

    def load_image(self, path):
        if not os.path.exists(path):
            self.update_status("File not found.", "#ef4444")
            return
        try:
            dest = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                LIVE_CHART_PATH
            )
            shutil.copy(path, dest)
            self.chart_image.source = dest
            self.chart_image.reload()
            self.update_status(
                "Chart loaded. Analysing...", "#f59e0b")
            self.options_layout.height = dp(0)
            self.result_layout.height = dp(0)
            self.result_layout.clear_widgets()
            threading.Thread(
                target=self.run_analysis,
                args=(dest,),
                daemon=True
            ).start()
        except Exception as e:
            self.update_status(f"Error: {e}", "#ef4444")

    def run_analysis(self, path):
        try:
            result = analyse_chart(path)
        except Exception as e:
            result = None
            print(f"Analysis error: {e}")
        Clock.schedule_once(lambda dt: self.on_analysis_done(result))

    def on_analysis_done(self, result):
        if result:
            self.current_analysis = result
            try:
                draw_levels(result)
                save_analysis(result, ANALYZED_IMAGE_PATH)
            except Exception as e:
                print(f"Post analysis error: {e}")
            self.update_status(
                "Analysis complete — choose view below", "#10b981")
            self.options_layout.height = dp(220)
            self.load_history()
        else:
            self.update_status(
                "Analysis failed. Try again.", "#ef4444")

    def show_image_result(self, instance):
        if not self.current_analysis:
            return
        self.result_layout.clear_widgets()
        self.result_layout.height = dp(300)
        try:
            img_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                ANALYZED_IMAGE_PATH
            )
            img = Image(
                source=img_path,
                size_hint=(1, None),
                height=dp(220),
                allow_stretch=True,
                keep_ratio=True
            )
            img.reload()
            levels = GridLayout(
                cols=4,
                size_hint=(1, None),
                height=dp(60),
                spacing=dp(4)
            )
            a = self.current_analysis
            for label, value, color in [
                ("ENTRY", a.get("entry", "-"), "#00bfff"),
                ("SL", a.get("stop_loss", "-"), "#ef4444"),
                ("TP", a.get("take_profit", "-"), "#10b981"),
                ("R:R", a.get("risk_reward", "-"), "#f59e0b"),
            ]:
                col = BoxLayout(orientation='vertical')
                col.add_widget(make_label(
                    label, color=GRAY, size=9,
                    bold=True, align='center'))
                col.add_widget(make_label(
                    value,
                    color=get_color_from_hex(color),
                    size=11, bold=True, align='center'))
                levels.add_widget(col)
            self.result_layout.add_widget(img)
            self.result_layout.add_widget(levels)
        except Exception as e:
            self.result_layout.add_widget(
                make_label(f"Error: {e}", color=RED))

    def show_description(self, instance):
        if not self.current_analysis:
            return
        deep = self.current_analysis.get(
            "deep_analysis", "No analysis available.")
        self.result_layout.clear_widgets()
        self.result_layout.height = dp(400)
        scroll = ScrollView(size_hint=(1, None), height=dp(400))
        box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(8)
        )
        box.bind(minimum_height=box.setter('height'))
        box.add_widget(make_label(
            "Full Analysis", color=GOLD,
            size=13, bold=True))
        box.add_widget(make_label(deep, color=WHITE, size=11))
        scroll.add_widget(box)
        self.result_layout.add_widget(scroll)

    def show_direction(self, instance):
        if not self.current_analysis:
            return
        direction = self.current_analysis.get("direction", "NEUTRAL")
        color = ("#10b981" if direction == "BUY"
                 else "#ef4444" if direction == "SELL"
                 else "#94a3b8")
        self.result_layout.clear_widgets()
        self.result_layout.height = dp(120)
        badge = Label(
            text=direction,
            font_size=dp(48),
            bold=True,
            color=get_color_from_hex(color),
            size_hint=(1, None),
            height=dp(120)
        )
        self.result_layout.add_widget(badge)

    def update_status(self, text, color_hex):
        self.status_label.text = text
        self.status_label.color = get_color_from_hex(color_hex)

    def load_history(self):
        self.history_layout.clear_widgets()
        try:
            history = load_history()
        except Exception:
            history = []
        if not history:
            self.history_layout.add_widget(
                make_label("No history yet.", color=GRAY, size=12))
            self.history_layout.height = dp(40)
            return
        total_height = 0
        for h in history[:10]:
            direction = h.get("direction", "-")
            color = ("#10b981" if direction == "BUY"
                     else "#ef4444" if direction == "SELL"
                     else "#94a3b8")
            row = BoxLayout(
                size_hint=(1, None),
                height=dp(44),
                spacing=dp(8),
                padding=dp(8)
            )
            with row.canvas.before:
                Color(*BG2)
                rect = Rectangle(pos=row.pos, size=row.size)
            row.bind(pos=lambda i, v, r=rect: setattr(r, 'pos', v))
            row.bind(size=lambda i, v, r=rect: setattr(r, 'size', v))
            row.add_widget(make_label(
                direction,
                color=get_color_from_hex(color),
                size=11, bold=True))
            row.add_widget(make_label(
                h.get("timestamp", ""),
                color=GRAY, size=10))
            row.add_widget(make_label(
                f"R:R {h.get('risk_reward', '-')}",
                color=GOLD, size=10, align='right'))
            self.history_layout.add_widget(row)
            total_height += dp(44)
        self.history_layout.height = total_height


class ChartMindApp(App):
    def build(self):
        self.title = "ChartMind AI"
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        return sm


if __name__ == '__main__':
    ChartMindApp().run()