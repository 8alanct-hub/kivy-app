from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
import json
import os

ARCHIVO_PROGRESO = "progreso.json"

materias = {
    "Cálculo Diferencial": 7 + 20/60,
    "Programación": 3 + 20/60,
    "Estadística y Probabilidad": 7,
    "Álgebra Lineal": 5 + 20/60
}

def cargar_progreso():
    datos = {materia: 0 for materia in materias}
    if os.path.exists(ARCHIVO_PROGRESO):
        with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f:
            guardado = json.load(f)
            for materia in datos:
                if materia in guardado:
                    datos[materia] = guardado[materia]
    return datos

def guardar_progreso(progreso):
    with open(ARCHIVO_PROGRESO, "w", encoding="utf-8") as f:
        json.dump(progreso, f, ensure_ascii=False, indent=2)

class Tracker(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(10)
        self.padding = dp(10)

        self.progreso = cargar_progreso()
        self.barras = {}
        self.entradas = {}
        self.etiquetas = {}

        for materia in materias:
            self.add_widget(Label(text=materia, bold=True, font_size=18))

            barra = ProgressBar(max=100)
            self.barras[materia] = barra
            self.add_widget(barra)

            fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))

            entrada = TextInput(hint_text="Horas", input_filter="float", size_hint_x=0.3)
            self.entradas[materia] = entrada
            fila.add_widget(entrada)

            boton = Button(text="+", size_hint_x=0.2)
            boton.bind(on_release=lambda btn, m=materia: self.agregar_horas(m))
            fila.add_widget(boton)

            self.add_widget(fila)

            etiqueta = Label(text="", font_size=14)
            self.etiquetas[materia] = etiqueta
            self.add_widget(etiqueta)

            self.actualizar_barra(materia)

        boton_reset = Button(text="Reiniciar semana", background_color=(1, 0, 0, 1))
        boton_reset.bind(on_release=self.reiniciar_semana)
        self.add_widget(boton_reset)

    def agregar_horas(self, materia):
        try:
            horas = float(self.entradas[materia].text)
            if horas <= 0:
                return
            self.progreso[materia] += horas
            if self.progreso[materia] > materias[materia]:
                self.progreso[materia] = materias[materia]
            self.actualizar_barra(materia)
            guardar_progreso(self.progreso)
            self.entradas[materia].text = ""
        except ValueError:
            self.mostrar_popup("Error", "Introduce un número válido.")

    def actualizar_barra(self, materia):
        meta = materias[materia]
        valor = self.progreso[materia]
        porcentaje = (valor / meta) * 100
        self.barras[materia].value = porcentaje
        self.etiquetas[materia].text = f"{valor:.2f}h / {meta:.2f}h ({porcentaje:.1f}%)"

    def reiniciar_semana(self, instance):
        def confirmar(_):
            for materia in self.progreso:
                self.progreso[materia] = 0
                self.actualizar_barra(materia)
            guardar_progreso(self.progreso)
            popup.dismiss()

        popup = Popup(title="Confirmar",
                      content=BoxLayout(orientation='vertical', children=[
                          Label(text="¿Seguro que quieres reiniciar todas las horas a 0?"),
                          Button(text="Sí", on_release=confirmar),
                          Button(text="No", on_release=lambda _: popup.dismiss())
                      ]),
                      size_hint=(0.6, 0.4))
        popup.open()

    def mostrar_popup(self, titulo, mensaje):
        popup = Popup(title=titulo,
                      content=Label(text=mensaje),
                      size_hint=(0.6, 0.3))
        popup.open()

class TrackerApp(App):
    def build(self):
        return Tracker()

if __name__ == "__main__":
    TrackerApp().run()
