from kivy.uix.screenmanager import Screen
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.app import App
from kivy.uix.label import Label
import matplotlib.pyplot as plt
import json


class ResultsScreen(Screen):
    def on_enter(self):
        self.ids.graph_box.clear_widgets()

        try:
            with open("availability.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ids.graph_box.add_widget(Label(text="No data to show"))
            return

        # Count votes
        counter = {}
        for user, schedule in data.items():
            for day, times in schedule.items():
                for time in times:
                    key = f"{day.capitalize()} - {time.capitalize()}"
                    counter[key] = counter.get(key, 0) + 1

        if not counter:
            self.ids.graph_box.add_widget(Label(text="No votes found"))
            return

        # Sort keys alphabetically for consistent graph
        labels = sorted(counter.keys())
        values = [counter[label] for label in labels]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(labels, values, color="skyblue")
        ax.set_xlabel("Cantidad de votos")
        ax.set_title("Resultados de disponibilidad para reunión")
        fig.tight_layout()

        self.ids.graph_box.add_widget(FigureCanvasKivyAgg(fig))
        #canvas = FigureCanvasKivyAgg(fig)
        #self.ids.graph_box.add_widget(canvas)
