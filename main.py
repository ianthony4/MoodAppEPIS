from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
# Para el anuncio emergente
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from json.decoder import JSONDecodeError
from datetime import datetime
import json, glob, random
from pathlib import Path
from results_screen import ResultsScreen # Para la grafica

# For button-hover feature
from hoverable import HoverBehavior



class LoginScreen(Screen):
    def sign_up(self):
        self.manager.current = "sign_up_screen"

    def login(self, uname, pwd):
        try:
            with open("users.json", "r") as file:
                users = json.load(file)

        except (FileNotFoundError, JSONDecodeError):
            self.ids.login_wrong.text = "No se encuentra el usuario"
            return

        if uname in users and users[uname]['password'] == pwd:
            App.get_running_app().current_user = uname
            self.manager.current = "login_success"
        else:
            self.ids.login_wrong.text = 'Usuario o Contraseña Invalido'

class LoginSuccessScreen(Screen):
    def logout(self):
        self.manager.transition.direction = 'right'
        self.manager.current = "login_screen"

    def display_quote(self, feel):
        feel = feel.lower()
        available_feelings = [Path(f).stem for f in glob.glob("files/*.txt")]

        if feel in available_feelings:
            with open(f"files/{feel}.txt", encoding="utf8") as file:
                quotes = file.readlines()
            self.ids.quote.text = random.choice(quotes).strip()
        else:
            self.ids.quote.text = "Prueba otra emocion"
    def show_best_time(self):
        try:
            with open("availability.json", "r") as file:
                data = json.load(file)
        except (FileNotFoundError, JSONDecodeError):
            self.ids.quote.text = "No availability data found."
            return

        counter = {}

        # Contar votos
        for user, schedule in data.items():
            for day, times in schedule.items():
                for time in times:
                    key = f"{day} {time}"
                    counter[key] = counter.get(key, 0) + 1

        if not counter:
            self.ids.quote.text = "No availabilities submitted yet."
            return

        # Obtener la opción más votada
        best_option = max(counter.items(), key=lambda x: x[1])
        best_time, votes = best_option

        self.ids.quote.text = f"Mejor opción: {best_time.capitalize()} ({votes} votos)"

class SignupScreen(Screen):
    def add_user(self, uname, pwd):
        try:
            with open("users.json", "r") as file:
                users = json.load(file)
        except (FileNotFoundError, JSONDecodeError):
            users = {}

        users[uname] = {
            'username': uname,
            'password': pwd,
            'created': datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        }

        with open("users.json", "w") as file:
            json.dump(users, file, indent=4)

        self.manager.current = "sign_up_success"

class SignupSuccessScreen(Screen):
    def login_page(self):
        self.manager.transition.direction = 'right'
        self.manager.current = "login_screen"

class ScheduleScreen(Screen):

    def show_popup(self, message):
        popup = Popup(title='Aviso',
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200))
        popup.open()
    
    def save_availability(self,
                          mon_morn, mon_aft, mon_eve,
                          tue_morn, tue_aft, tue_eve,
                          wed_morn, wed_aft, wed_eve,
                          thu_morn, thu_aft, thu_eve,
                          fri_morn, fri_aft, fri_eve,
                          sat_morn, sat_aft, sat_eve,
                          sun_morn, sun_aft, sun_eve):
        
        username = App.get_running_app().current_user

        availability = {
            "Lunes": self._get_times(mon_morn, mon_aft, mon_eve),
            "Martes": self._get_times(tue_morn, tue_aft, tue_eve),
            "Miercoles": self._get_times(wed_morn, wed_aft, wed_eve),
            "Jueves": self._get_times(thu_morn, thu_aft, thu_eve),
            "Viernes": self._get_times(fri_morn, fri_aft, fri_eve),
            "Sabado": self._get_times(sat_morn, sat_aft, sat_eve),
            "Domingo": self._get_times(sun_morn, sun_aft, sun_eve)
        }

        try:
            with open("availability.json", "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        if username in data:
            self.show_popup("Ya has enviado tu disponibilidad.\nSolo puedes votar una vez.")
            print(f"[INFO] Usuario '{username}' ya ha votado.")
            return 

        data[username] = availability

        with open("availability.json", "w") as file:
            json.dump(data, file, indent=4)

        self.show_popup("¡Tu disponibilidad ha sido registrada con éxito!")
        print(f"[INFO] Disponibilidad de '{username}' guardada correctamente.")
        self.manager.current = "login_success"  # o a una pantalla de confirmación

    def _get_times(self, morning, afternoon, evening):
        result = []
        if morning:
            result.append("Mañana")
        if afternoon:
            result.append("Tarde")
        if evening:
            result.append("Noche")
        return result

class ImageButton(ButtonBehavior, HoverBehavior, Image):
    pass
# Load Kivy design
Builder.load_file("design.kv")

class RootWidget(ScreenManager):
    pass

class MainApp(App):
    current_user = None
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MainApp().run()
