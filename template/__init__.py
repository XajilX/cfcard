from abc import ABC, abstractmethod
from PIL import Image
import sys, os

class Itemplate(ABC):
    @abstractmethod
    def generate(self, name: str, rank: str, rating: int, link_avatar: str) -> Image:
        pass
    @abstractmethod
    def fail(self, msg: str) -> Image:
        pass

from .tempdefault import TempDefault
from .tempdark import TempDark

class TemplateGetter():
    def __init__(self) -> None:
        self.__temps = {
            'default': TempDefault,
            'dark': TempDark
        }
    def getTemplate(self, name: str) -> Itemplate:
        if name not in self.__temps:
            return TempDefault()
        else:
            return self.__temps[name]()