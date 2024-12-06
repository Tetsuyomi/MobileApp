import os
import cv2
import requests
import numpy as np
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.camera import Camera
from kivy.graphics.texture import Texture
from datetime import datetime


class TomatoApp(App):

    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Выпадающий список для выбора объекта
        self.spinner = Spinner(
            text="Выберите овощ/фрукт",
            values=("Помидор", "Яблоко", "Банан"),
            size_hint=(1, 0.1),
        )
        self.layout.add_widget(self.spinner)

        # Кнопка для запуска камеры
        self.capture_button = Button(
            text="Открыть камеру",
            size_hint=(1, 0.1),
        )
        self.capture_button.bind(on_press=self.open_camera)
        self.layout.add_widget(self.capture_button)

        # Метка для результата
        self.result_label = Label(
            text="Результат",
            size_hint=(1, 0.1)
        )
        self.layout.add_widget(self.result_label)

        return self.layout

    def open_camera(self, instance):
        # Открываем камеру
        self.camera = Camera(play=True)
        self.layout.add_widget(self.camera)

        # Меняем функционал кнопки
        self.capture_button.text = "Сделать фото"
        self.capture_button.unbind(on_press=self.open_camera)
        self.capture_button.bind(on_press=self.capture_image)

    def capture_image(self, instance):
        # Захватываем изображение
        if self.camera.texture:
            # Получаем изображение в формате numpy
            img = self.texture_to_numpy(self.camera.texture)

            # Создаем уникальное имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"captured_image_{timestamp}.jpg"
            cv2.imwrite(image_path, img)  # Сохраняем снимок

            # Отправляем изображение на сервер
            self.send_image_to_server(image_path)

            # Удаляем камеру после захвата
            self.layout.remove_widget(self.camera)
            self.capture_button.text = "Открыть камеру"
            self.capture_button.unbind(on_press=self.capture_image)
            self.capture_button.bind(on_press=self.open_camera)

            # Удаляем временный файл
            if os.path.exists(image_path):
                os.remove(image_path)

    def texture_to_numpy(self, texture):
        # Преобразуем текстуру Kivy в массив NumPy
        size = texture.size
        pixels = texture.pixels
        img = np.frombuffer(pixels, dtype=np.uint8).reshape(size[1], size[0], 4)
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    def send_image_to_server(self, image_path):
        url = "http://localhost:5000/upload"  # URL сервера (в этом примере сервер на локальном хосте)
        try:
            files = {'file': open(image_path, 'rb')}
            response = requests.post(url, files=files)

            if response.status_code == 200:
                self.result_label.text = "Изображение успешно отправлено!"
            else:
                self.result_label.text = f"Ошибка при отправке изображения: {response.status_code}"
        except Exception as e:
            self.result_label.text = f"Ошибка: {e}"


if __name__ == '__main__':
    TomatoApp().run()
