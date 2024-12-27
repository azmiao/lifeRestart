from typing import List

from .Talent import Talent


class WeightedEvent:
    def __init__(self, o: str):
        if '*' not in o:
            self.weight: float = 1.0
            self.evt: int = int(o)
        else:
            s = o.split('*')
            self.weight: float = float(s[1])
            self.evt: int = int(s[0])


class AgeManager:
    ages = None

    @staticmethod
    def load(config):
        AgeManager.ages = config
        for a in AgeManager.ages:
            if 'event' in AgeManager.ages[a]:
                AgeManager.ages[a]['event'] = [WeightedEvent(str(x)) for x in AgeManager.ages[a]['event']]

    def __init__(self, base):
        self._base = base

    def _get_now(self):
        return AgeManager.ages[str(self._base.property.AGE)]

    def getEvents(self) -> List[WeightedEvent]:
        now = self._get_now()
        if 'event' in now:
            return now['event']
        return []

    def getTalents(self) -> List[Talent]:
        now = self._get_now()
        if 'talent' in now:
            return now['talent']
        return []

    def grow(self):
        self._base.property.AGE += 1
