import numpy as np
import random

class BitCrusher:
    MODE_STANDARD = 0
    MODE_SMOOTH = 1
    MODE_AVERAGE = 2
    
    def __init__(self, rate: float = (1/44100)*3, mode: int = MODE_STANDARD, delta: float = 1/44100, randomness=0):
        """
        Инициализация биткрашера
        
        Args:
            rate: частота дробления (секунды)
            mode: режим работы (0 - стандартный, 1 - сглаженный, 2 - усреднение)
            delta: шаг времени (по умолчанию 1/44100 для аудио 44.1 кГц)
        """
        self.rate = rate
        self.mode = mode
        self.delta = delta
        
        # Общие атрибуты
        self.v = 0.0
        self.t = 0.0
        self.rand = randomness*0.001
        
        # Атрибуты для сглаженного режима
        self.p1 = 0
        self.p2 = 0
        self.pt = 0
        
        # Атрибуты для режима усреднения
        self.data = np.array([])
        
    def set_rate(self, rate: float):
        """Установить частоту дробления"""
        self.rate = rate
        
    def set_mode(self, mode: int):
        """Установить режим работы"""
        self.mode = mode
        # Сброс состояния при смене режима
        if mode == self.MODE_AVERAGE:
            self.data = np.array([])
        elif mode == self.MODE_SMOOTH:
            self.p1, self.p2 = 1.0, 1.0
            
    def set_randomness(self, randomness: float):
        """Установить уровень случайности (0-1)"""
        self.rand = randomness * 1000  # Масштабирование для совместимости
        
    def _get_random_offset(self) -> float:
        """Получить случайное смещение времени"""
        if self.rand > 0:
            return random.random() * 0.001 * self.rand
        return 0.0
    
    def _tick_standard(self, value: float) -> float:
        """Стандартный режим: удерживание последнего значения"""
        self.t += self.delta
        
        if self.t >= self.rate:
            self.t -= self.rate + self._get_random_offset()
            self.v = value
            
        return self.v
    
    def _tick_smooth(self, value: float) -> float:
        """Сглаженный режим: линейная интерполяция между значениями"""
        self.t += self.delta
        
        if self.t >= self.rate:
            self.t -= self.rate + self._get_random_offset()
            self.p1 = self.p2
            self.p2 = value
            
        # Линейная интерполяция между p1 и p2
        return ((self.p2 - self.p1) * self.t) / self.rate + self.p1
    
    def _tick_average(self, value: float) -> float:
        """Режим усреднения: среднее значение за период"""
        self.t += self.delta
        self.data = np.append(self.data, value)
        
        if self.t >= self.rate:
            self.t -= self.rate + self._get_random_offset()
            self.v = np.mean(self.data)
            self.data = np.array([])
            
        return self.v
    
    def tick(self, value: float) -> float:
        """
        Обработка одного сэмпла
        
        Args:
            value: входное значение
            
        Returns:
            Обработанное значение
        """
        if self.mode == self.MODE_SMOOTH:
            return self._tick_smooth(value)
        elif self.mode == self.MODE_AVERAGE:
            return self._tick_average(value)
        else:  # MODE_STANDARD по умолчанию
            return self._tick_standard(value)
    
    def reset(self):
        """Сброс состояния процессора"""
        self.t = 0.0
        self.v = 0.0
        self.data = np.array([])
        self.p1, self.p2 = 1.0, 1.0
        
    def get_current_mode_name(self) -> str:
        """Получить название текущего режима"""
        modes = {
            self.MODE_STANDARD: "Standard",
            self.MODE_SMOOTH: "Smooth",
            self.MODE_AVERAGE: "Average"
        }
        return modes.get(self.mode, "Unknown")