# -*- coding: utf-8 -*-
"""Observer pattern in Python.

Inspired from http://www.giantflyingsaucer.com/blog/?p=5117

TODO:

"""

from abc import ABCMeta, abstractmethod


class Observable(object):
    def __init__(self):
        self.observers = []

    def register(self, observer):
        if not observer in self.observers:
            self.observers.append(observer)

    def unregister(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def unregister_all(self):
        if self.observers:
            del self.observers[:]

    def update_observers(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(*args, **kwargs)


class Observer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

