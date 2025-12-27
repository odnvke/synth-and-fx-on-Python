import pyglet
import numpy as np
import wave
import struct
from pyglet import shapes
from pyglet.window import key
import sys
import os

class WavOscilloscope:
    def __init__(self, wav_file):
        self.window = pyglet.window.Window(1200, 700, caption=f"WAV Oscilloscope - {os.path.basename(wav_file)}")
        
        # Сохраняем имя файла
        self.filename = wav_file
        
        # Загружаем и анализируем WAV файл
        self.wave_data = self.load_wav_file(wav_file)
        
        # Настройки отображения
        self.channel_colors = [(0, 200, 255), (255, 100, 0), (0, 255, 150), (255, 255, 0)]
        
        # Настройки зума и скролла
        self.zoom_level = 1.0  # 1.0 = полный просмотр
        self.scroll_position = 0.0  # 0.0 = начало, 1.0 = конец
        self.time_window = 1.0  # секунды отображаемого времени
        self.max_zoom = 1000.0  # Максимальный зум увеличен
        
        # Создаем элементы управления
        self.create_controls()
        
        # Получаем данные для волновой формы
        self.update_waveform_display()
        
        # Обработчики событий
        @self.window.event
        def on_draw():
            self.window.clear()
            self.draw_grid()
            self.draw_waveform()
            self.draw_controls()
            self.draw_info()
        
        @self.window.event
        def on_key_press(symbol, modifiers):
            # Управление зумом
            if symbol == key.PLUS or symbol == key.EQUAL:
                self.zoom_in()
            elif symbol == key.MINUS:
                self.zoom_out()
            elif symbol == key.HOME:
                self.reset_view()
            elif symbol == key.LEFT:
                self.scroll_left()
            elif symbol == key.RIGHT:
                self.scroll_right()
            elif symbol == key.UP:
                self.zoom_in()
            elif symbol == key.DOWN:
                self.zoom_out()
            elif symbol == key.ESCAPE:
                pyglet.app.exit()
        
        @self.window.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            # Зум колесиком мыши
            if scroll_y > 0:
                self.zoom_in()
            elif scroll_y < 0:
                self.zoom_out()
        
        @self.window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            # Скролл перетаскиванием (скорость зависит от зума)
            if buttons & pyglet.window.mouse.LEFT:
                # Чем больше зум, тем медленнее скролл
                scroll_speed = 0.5 / self.zoom_level
                self.scroll_by_pixels(-dx * scroll_speed)
    
    def load_wav_file(self, filename):
        """Загружаем и анализируем WAV файл с помощью wave module"""
        try:
            with wave.open(filename, 'rb') as wav_file:
                # Получаем параметры
                params = wav_file.getparams()
                n_channels = params.nchannels
                sampwidth = params.sampwidth
                framerate = params.framerate
                n_frames = params.nframes
                
                # Читаем все фреймы
                frames = wav_file.readframes(n_frames)
                
                # Определяем формат данных на основе sampwidth
                if sampwidth == 1:
                    fmt = f"{n_frames * n_channels}B"  # unsigned char
                    data = struct.unpack(fmt, frames)
                    # Конвертируем в signed
                    data = [(d - 128) for d in data]
                elif sampwidth == 2:
                    fmt = f"{n_frames * n_channels}h"  # signed short
                    data = struct.unpack(fmt, frames)
                elif sampwidth == 3:
                    # 24-bit требует специальной обработки
                    data = []
                    for i in range(0, len(frames), 3):
                        sample = struct.unpack('<i', frames[i:i+3] + b'\x00')[0]
                        if sample >= 0x800000:
                            sample -= 0x1000000
                        data.append(sample)
                else:
                    fmt = f"{n_frames * n_channels}i"  # signed int
                    data = struct.unpack(fmt, frames)
                
                # Реорганизуем данные по каналам
                if n_channels > 1:
                    channels = [[] for _ in range(n_channels)]
                    for i in range(0, len(data), n_channels):
                        for ch in range(n_channels):
                            if i + ch < len(data):
                                channels[ch].append(data[i + ch])
                    wave_data = {
                        'channels': channels,
                        'params': params,
                        'sampwidth': sampwidth,
                        'framerate': framerate,
                        'duration': n_frames / framerate
                    }
                else:
                    wave_data = {
                        'channels': [data],
                        'params': params,
                        'sampwidth': sampwidth,
                        'framerate': framerate,
                        'duration': n_frames / framerate
                    }
                
                return wave_data
                
        except Exception as e:
            print(f"Ошибка загрузки WAV файла: {e}")
            return None
    
    def create_controls(self):
        """Создаем элементы управления"""
        # Текст информации о зуме
        self.zoom_text = pyglet.text.Label(f"Zoom: {self.zoom_level:.1f}x", 
                                          x=50, y=650, 
                                          font_size=14, 
                                          color=(200, 200, 200, 255))
        
        # Текст информации о позиции
        self.position_text = pyglet.text.Label(f"Position: {self.scroll_position:.1%}", 
                                              x=200, y=650, 
                                              font_size=14, 
                                              color=(200, 200, 200, 255))
        
        # Текст времени отображения
        self.time_text = pyglet.text.Label(f"Window: {self.time_window:.3f}s", 
                                          x=350, y=650, 
                                          font_size=14, 
                                          color=(200, 200, 200, 255))
    
    def update_waveform_display(self):
        """Обновляем отображение волновой формы с учетом зума и скролла"""
        if not self.wave_data:
            return
        
        # Вычисляем диапазон сэмплов для отображения
        total_samples = len(self.wave_data['channels'][0])
        start_sample = int(self.scroll_position * total_samples)
        
        # Количество сэмплов для отображения с учетом зума
        display_samples = int(total_samples / self.zoom_level)
        end_sample = min(start_sample + display_samples, total_samples)
        
        # Ограничиваем window size
        actual_display_samples = end_sample - start_sample
        if actual_display_samples <= 0:
            return
        
        # Обновляем time_window
        self.time_window = actual_display_samples / self.wave_data['framerate']
        
        self.channel_points = []
        
        # Общие настройки для всех каналов
        base_y = 350  # Все каналы на одном уровне по центру
        display_height = 300  # Общая высота отображения
        
        # Находим общие min и max по всем каналам для нормализации
        all_display_data = []
        for channel_data in self.wave_data['channels']:
            all_display_data.extend(channel_data[start_sample:end_sample])
        
        if not all_display_data:
            return
            
        global_min = min(all_display_data)
        global_max = max(all_display_data)
        global_range = global_max - global_min
        if global_range == 0:
            global_range = 1
        
        for ch_idx, channel_data in enumerate(self.wave_data['channels']):
            # Берем только отображаемые сэмплы
            display_data = channel_data[start_sample:end_sample]
            
            if len(display_data) < 2:
                continue
            
            # Определяем шаг для дискретизации
            max_points = 1000  # Увеличили для более плавного отображения при зуме
            step = max(1, len(display_data) // max_points)
            
            color = self.channel_colors[ch_idx % len(self.channel_colors)]
            
            # Сохраняем точки для отрисовки
            points = []
            for i in range(0, len(display_data), step):
                sample_idx = i
                if sample_idx >= len(display_data):
                    break
                    
                sample = display_data[sample_idx]
                
                # Нормализуем относительно глобальных min/max
                normalized = (sample - global_min) / global_range
                
                # Вычисляем координаты (все каналы на одном уровне)
                x = 100 + (sample_idx / len(display_data)) * 1000
                y = base_y + (normalized - 0.5) * display_height  # Центрируем
                
                points.append((x, y))
            
            self.channel_points.append((points, color))
    
    def draw_waveform(self):
        """Рисуем волновую форму"""
        if not hasattr(self, 'channel_points'):
            return
        
        for points, color in self.channel_points:
            if len(points) < 2:
                continue
            
            # Рисуем линию через все точки
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                
                # Прямая отрисовка линии
                try:
                    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                        ('v2f', (x1, y1, x2, y2)),
                                        ('c3B', color + color))
                except:
                    # Fallback
                    try:
                        shapes.Line(x1, y1, x2, y2, color=color).draw()
                    except:
                        # Простой прямоугольник как линия
                        width = max(1, 2 / self.zoom_level)  # Толщина зависит от зума
                        if abs(x2 - x1) > abs(y2 - y1):
                            height = width
                            shapes.Rectangle(min(x1, x2), y1 - height/2, 
                                           abs(x2 - x1), height, 
                                           color=color).draw()
                        else:
                            shapes.Rectangle(x1 - width/2, min(y1, y2), 
                                           width, abs(y2 - y1), 
                                           color=color).draw()
    
    def draw_grid(self):
        """Рисуем сетку осциллографа"""
        # Горизонтальные линии
        for i in range(-200, 201, 50):
            y = 350 + i
            if 100 <= y <= 600:
                gray = (50, 50, 50)
                try:
                    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                        ('v2f', (100, y, 1100, y)),
                                        ('c3B', gray + gray))
                except:
                    shapes.Line(100, y, 1100, y, color=gray).draw()
        
        # Вертикальные линии
        for i in range(0, 1001, 100):
            x = 100 + i
            gray = (50, 50, 50)
            try:
                pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                    ('v2f', (x, 100, x, 600)),
                                    ('c3B', gray + gray))
            except:
                shapes.Line(x, 100, x, 600, color=gray).draw()
        
        # Центральные оси
        gray = (150, 150, 150)  # Ярче центральные линии
        try:
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                ('v2f', (100, 350, 1100, 350)),
                                ('c3B', gray + gray))
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                ('v2f', (600, 100, 600, 600)),
                                ('c3B', gray + gray))
        except:
            shapes.Line(100, 350, 1100, 350, color=gray).draw()
            shapes.Line(600, 100, 600, 600, color=gray).draw()
    
    def draw_controls(self):
        """Рисуем элементы управления"""
        self.zoom_text.draw()
        self.position_text.draw()
        self.time_text.draw()
    
    def draw_info(self):
        """Рисуем информацию о файле"""
        if not self.wave_data:
            error_label = pyglet.text.Label("Ошибка загрузки файла", x=600, y=350, 
                                           font_size=24, anchor_x='center', anchor_y='center',
                                           color=(255, 50, 50, 255))
            error_label.draw()
            return
        
        params = self.wave_data['params']
        
        # Только основная информация
        info_text = [
            f"Файл: {os.path.basename(self.filename)}",
            f"Каналы: {params.nchannels}",
            f"Частота: {params.framerate} Гц",
            f"Длительность: {self.wave_data['duration']:.3f} сек",
            f"Отображаем: {self.time_window:.6f} сек",
            f"Зум: {self.zoom_level:.1f}x"
        ]
        
        for i, line in enumerate(info_text):
            label = pyglet.text.Label(line, x=50, y=620 - i*20, 
                                     font_size=12, 
                                     color=(200, 200, 200, 255))
            label.draw()
        
        # Инструкции
        instructions = [
            "УПРАВЛЕНИЕ:",
            "+ / Колесико вверх: Увеличить зум",
            "- / Колесико вниз: Уменьшить зум",
            "← →: Скролл по времени",
            "HOME: Сброс вида",
            "ЛКМ + перетаскивание: Плавный скролл",
            "ESC: Выход"
        ]
        
        for i, instruction in enumerate(instructions):
            label = pyglet.text.Label(instruction, x=800, y=620 - i*20, 
                                     font_size=12, 
                                     color=(150, 200, 255, 255))
            label.draw()
    
    # Функции управления зумом и скроллом
    def zoom_in(self):
        """Увеличить зум"""
        self.zoom_level *= 1.5
        self.zoom_level = min(self.zoom_level, self.max_zoom)
        self.update_display()
    
    def zoom_out(self):
        """Уменьшить зум"""
        self.zoom_level /= 1.5
        self.zoom_level = max(self.zoom_level, 1.0)
        self.update_display()
    
    def reset_view(self):
        """Сбросить вид к начальному состоянию"""
        self.zoom_level = 1.0
        self.scroll_position = 0.0
        self.update_display()
    
    def scroll_left(self):
        """Скролл влево (скорость зависит от зума)"""
        scroll_amount = 0.1 / self.zoom_level  # Чем больше зум, тем меньше шаг
        self.scroll_position = max(0.0, self.scroll_position - scroll_amount)
        self.update_display()
    
    def scroll_right(self):
        """Скролл вправо (скорость зависит от зума)"""
        scroll_amount = 0.1 / self.zoom_level  # Чем больше зум, тем меньше шаг
        total_samples = len(self.wave_data['channels'][0]) if self.wave_data else 1
        display_samples = int(total_samples / self.zoom_level)
        max_scroll = max(0.0, 1.0 - display_samples / total_samples)
        self.scroll_position = min(max_scroll, self.scroll_position + scroll_amount)
        self.update_display()
    
    def scroll_by_pixels(self, dx):
        """Скролл на количество пикселей (скорость зависит от зума)"""
        # Чем больше зум, тем медленнее скролл
        scroll_amount = (dx / 1000.0) / self.zoom_level
        total_samples = len(self.wave_data['channels'][0]) if self.wave_data else 1
        display_samples = int(total_samples / self.zoom_level)
        max_scroll = max(0.0, 1.0 - display_samples / total_samples)
        
        self.scroll_position += scroll_amount
        self.scroll_position = max(0.0, min(max_scroll, self.scroll_position))
        self.update_display()
    
    def update_display(self):
        """Обновить отображение"""
        # Обновляем текстовые метки
        self.zoom_text.text = f"Zoom: {self.zoom_level:.1f}x"
        self.position_text.text = f"Position: {self.scroll_position:.1%}"
        self.time_text.text = f"Window: {self.time_window:.6f}s"
        
        # Обновляем отображение волновой формы
        self.update_waveform_display()
    
    def run(self):
        pyglet.app.run()

def main():
    wav_file = "out.wav"
    
    if not os.path.exists(wav_file):
        print(f"Ошибка: файл '{wav_file}' не найден")
        sys.exit(1)
    
    if not wav_file.lower().endswith('.wav'):
        print("Предупреждение: файл может не быть WAV файлом")
        response = input("Продолжить? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    oscilloscope = WavOscilloscope(wav_file)
    oscilloscope.run()

if __name__ == "__main__":
    main()