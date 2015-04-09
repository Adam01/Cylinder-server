from unittest import TestCase

__author__ = 'Adam'

import unittest
import os
import sys

from subject import EventSubject, EventRetainer


class test_callable:
    def __call__(self, callback):
        callback()

    def func(self, callback):
        callback()


class TestEventSubject(TestCase):
    def setUp(self):
        self.callback_count = 0

    def increment_count(self):
        self.callback_count += 1

    def test_cleanup(self):
        subject = EventSubject()
        obj = test_callable()
        subject.subscribe("something", obj.func)
        subject.subscribe("something", obj.func)
        del obj
        self.assertEquals(2, subject.cleanup())

    def test_count(self):
        subject = EventSubject()
        obj = test_callable()
        subject.subscribe("something", self.fail)
        subject.subscribe("something", self.fail)
        subject.subscribe("something", obj.func)
        subject.subscribe("something_else", self.fail)
        del obj
        self.assertEquals(2, subject.count("something"))
        self.assertEquals(1, subject.count("something_else"))

    def test_subscribe_and_notify(self):
        subject = EventSubject()
        obj = test_callable()

        subject.subscribe("something", obj)
        subject.subscribe("something", obj.func)
        subject.subscribe("something_else", self.fail)

        ret = subject.notify("something", self.increment_count)
        self.assertEqual(2, ret)
        self.assertEqual(2, self.callback_count)

        subject.notify("nothing", self.fail)





