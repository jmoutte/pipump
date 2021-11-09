from collections import deque
from statistics import mean

class PVSystem:
    _consumption_readings = deque([], maxlen=5)
    _production_readings = deque([], maxlen=5)

    @property
    def consumption(self):
        if not len(self._consumption_readings):
            return 0
        return mean(self._consumption_readings)
    
    @consumption.setter
    def consumption(self, value):
        self._consumption_readings.append(value)
    
    @consumption.deleter
    def consumption(self):
        self._consumption_readings.clear()

    @property
    def production(self):
        if not len(self._production_readings):
            return 0
        return mean(self._production_readings)
    
    @production.setter
    def production(self, value):
        self._production_readings.append(value)
    
    @production.deleter
    def production(self):
        self._production_readings.clear()
        