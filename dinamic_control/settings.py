import inspect
import warnings
from typing import Iterator

import pytest


def custom_warning_format(message, category, filename, lineno, line=None):
    return f"{category.__name__}: {message}\n"


warnings.formatwarning = custom_warning_format


class MetaBase(type):
    """
    Метакласс для базового класса настроек.
    """

    def __new__(cls, name, bases, dct):
        """
        Метод создания нового класса с объединением exclude_for_set.
        :param name:
        :param bases:
        :param dct:
        """
        new_class = super().__new__(cls, name, bases, dct)
        current_exclude = getattr(new_class.Meta, "exclude_for_set", [])
        parent_exclude = []
        for base in bases:
            if hasattr(base, "Meta") and hasattr(base.Meta, "exclude_for_set"):
                parent_exclude.extend(base.Meta.exclude_for_set)
        combined_exclude = list(set(current_exclude + parent_exclude))
        if not hasattr(new_class, "Meta"):
            new_class.Meta = type("Meta", (), {})
        new_class.Meta.exclude_for_set = combined_exclude
        return new_class


class BaseSettings(metaclass=MetaBase):
    """
    Базовый класс настроек для наследования.
    """
    obj = None

    class Meta:
        exclude_for_set = ["obj", "get_obj", "_method_implementation", "_presence_all_methods"]

    def get_obj(self, **kwargs):
        attrs = dict(inspect.getmembers(self.__class__, lambda x: not inspect.isroutine(x)))
        attrs = {
            k: v for k, v in attrs.items()
            if not k.startswith('_')  # Исключаем приватные атрибуты
               and not k.startswith('__')  # Исключаем классовые атрибуты
               and k != 'Meta'  # Исключаем класс 'Meta'
               and k not in self.Meta.exclude_for_set  # Исключаем атрибуты из списка exclude_for_set
        }
        if kwargs:
            attrs.update(kwargs)
        test_object = self.obj(**attrs)
        return test_object

    @pytest.fixture(scope="class", autouse=True)
    def _presence_all_methods(self) -> Iterator[None]:
        """
        Проверяет наличие всех требуемых методов тестирования. Выдает в отчет предупреждение об отсутствии методов.
        :return: None
        """
        class_methods = [method for method in dir(self.obj) if
                         not method.startswith('__') and callable(getattr(self.obj, method))]
        self_class_methods = [method for method in dir(self) if
                              not method.startswith('__') and callable(getattr(self, method))]
        self_methods = [method.removeprefix('test_') for method in self_class_methods]
        for method in class_methods:
            if not method in self_methods:
                class_file = inspect.getfile(self.__class__)
                class_line = inspect.getsourcelines(self.__class__)[1]
                warning_message = (
                    f"\nChecking class '{self.obj.__name__}'. Testing generated a warning:\n"
                    f"Method <test_{method}> has no implementation in class '{self.__class__.__name__}'\n"
                    f"  Class defined at {class_file}:{class_line}"
                )
                warnings.warn(warning_message, category=DeprecationWarning)
                # assert False, warning_message
        yield

    @pytest.fixture(scope="class", autouse=True)
    def _method_implementation(self) -> Iterator[None]:
        """
        Проверяет все ли методы тестирования имеют реализацию. Не гарантирует что проверенные методы имеют верную
        реализацию и охватывают собой все возможные результаты работы. Выдает предупреждение об отсутствии assert в
        проверяемом методе.
        :return: None
        """
        class_methods_implement = [method for method in dir(self) if
                                   not method.startswith('__') and callable(
                                       getattr(self,
                                               method)) and method not in self.Meta.exclude_for_set and method != "Meta" and method not in self.Meta.exclude_for_set]
        for method_name in class_methods_implement:
            method = getattr(self, method_name)
            source = inspect.getsource(method)
            if "assert" not in source:
                class_file = inspect.getfile(self.__class__)
                class_line = inspect.getsourcelines(self.__class__)[1]
                message_warning = (f"\nMethod <{method_name}> does not contain 'assert' in class '{self.__class__.__name__}'\n"
                                   f"  Class defined at {class_file}:{class_line}")
                warnings.warn(message_warning, category=DeprecationWarning)
                # assert False, message_warning
            else:
                method()
        yield

__all__ = ("BaseSettings",)