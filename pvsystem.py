from collections import deque
from statistics import mean

class PVSystem:
    _consumption_readings = deque([0], maxlen=5)
    _production_readings = deque([0], maxlen=5)

    @property
    def consumption(self):
        return mean(self._consumption_readings)
    
    @consumption.setter
    def consumption(self, value):
        self._consumption_readings.append(value)

    @property
    def production(self):
        return mean(self._production_readings)
    
    @production.setter
    def production(self, value):
        self._production_readings.append(value)
        