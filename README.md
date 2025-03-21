# DinamicMiniControlTest #

## Вступление 
Этот проект - не панацея, не замена coverage и ему подобным! Создавался для собственного удобства и использования.
Сразу после запуска тестов покажет в терминале какие методы не тестировались, позволяя не пользоваться постоянно
командами "coverage report" и "coverage html".

## Использование

#### Классы:
```python
class SomeBaseClass:
    type: str = None
    attr: str = None
    attr1: str = None
    attr2: str = None
    attr3: bool = False
    
    def __init__(self, *args: str, attr1: str = None, attr2: str = None, attr3: bool = False):
        if args:
            self.attr = args[0]
        self.attr1 = attr1
        self.attr2 = attr2
        self.attr3 = attr3
            
    def create_obj(self):
        self.attr5 = self.attr1 + ' ' + self.attr2
        return self.attr5
    
    def create_readonly_param(self):
        pass
    
    def availability_control(self):
        return "availability control"
    
    def implementation_control(self):
        return "implementation control"
    

class SomeClass(SomeBaseClass):
    type="text"
    
    def create_readonly_param(self):
        str = f' class="readonly"' if self.attr3 is True else ''
        return str
    
    
class SomeClass2(SomeBaseClass):
    type="text"
    
    def create_readonly_param(self):
        str = f' readonly' if self.attr3 is True else ''
        return str
```

#### Тестирование:
BaseSettings - базовый класс настроек для наследования основного класса. 
Создает объект тестирования с различными атрибутами "на лету" и проверяет наличие тестов для методов и их "реализацию"
(контролирует наличие хотя бы одного assert в методе тестирования).
Если в классе метод "implementation_control", то в тестах будет искать метод "test_implementation_control" и уже в нем
будет проверять наличие хотя бы одного"assert".
```python
# тесты наличия и реализации методов вынес в конкретные классы для наглядности показа предупреждений

from typing import Type
from functools import wraps

from dinamic_control import BaseSettings
from your_module import SomeBaseClass, SomeClass, SomeClass2


class BaseClassTest(BaseSettings):
    """
    Базовый класс настроек для наследования основного класса.
    """
    # Класс для тестирования.
    obj: Type[SomeBaseClass] = None
    # Базовые атрибуты для вызова класса.
    # Атрибут args создается списком для передачи содержимого как позиционные аргументы при вызове объекта тестирования,
    # можно указывать как в родительском, так и в дочернем классе. Args дочернего класса заменяет собой родительский.
    args = ["attr_args1", "attr_args2"]   
    # Атрибуты применяются как kwargs при вызове объекта тестирования. Так же имеют приоритет в указанные дочернем классе.
    attr1: str = "some_attr1"
    attr2: str = "some_attr2"
    attr3: bool = True
    # дополнительный атрибут(если требуется для тестирования, но в вызове класса не используется), в вызове будет проигнорирован
    attr4: bool = False

    class Meta:
        # attr4 будет проигнорирован при вызове объекта тестирования.
        exclude_for_set = ["attr4"]
    
    # Необязательный метод. Создан для удобства - добавляет подсказки при наборе self.get_obj() и "смотрит" за именами методов.
    @wraps(obj.__class__.__init__) # Замена аннотации args kwargs, не обязательный декоратор, можно и просто написать аннотацию.
    def get_obj(self, *args, **kwargs) -> obj:
        return super().get_obj(*args, **kwargs)
    
    # Общие методы тестирования класса, когда от наличия аргументов или их значения результат не поменяется.
    def test_init_obj(self): 
        # Вызов объекта тестирования с аргументами. В данном случае аргументами будут атрибуты класса
        # за исключением attr4, который указан в "exclude_for_set = ["attr4"]".
        obj = self.get_obj()  
        assert isinstance(obj.__class__, self.obj.__class__)
        assert obj.attr == "attr_args1"
        assert obj.attr1 == "some_attr1"
        assert obj.attr2 == "some_attr2"
        assert obj.attr3 is True
        assert obj.create_obj == 'some_attr1 some_attr2'
        assert obj.attr5 == 'some_attr1 some_attr2'
        # Аргументы можно менять и продолжать тестирование. 
        # Не очевидный момент - позиционный аргумент указанный в вызове полностью заменят атрибут класса args,
        # тогда как именованный дополняет или заменяет только самого себя!
        obj = self.get_obj("attr_args_new", attr1="new_attr1")
        assert obj.attr == 'attr_args_new'
        assert obj.create_obj == 'new_attr1 some_attr2'
        assert obj.attr5 == 'new_attr1 some_attr2'
        
        
class TestSomeClass(BaseClassTest):
    """
    Тестирование частных методов классов.
    """
    obj = SomeClass

    def test_create_readonly_param(self):
        # в разных классах результат может различаться в зависимости от аргумента в вызове объекта
        obj = self.get_obj()
        assert obj.create_readonly_param() == ' class="readonly'
        obj = self.get_obj(attr3=False)
        assert obj.create_readonly_param() == ''
        
    def test_availability_control(self):
        obj = self.get_obj()
        assert obj.availability_control() == "availability control"
    
    def test_implementation_control(self):
        obj = self.get_obj()
        assert obj.implementation_control() == "implementation control"

class TestSomeClass2(BaseClassTest):
    obj = SomeClass2
    args = ["args some_class2",]

    def test_create_readonly_param(self):
        # в разных классах результат может различаться в зависимости от аргумента в вызове объекта
        obj = self.get_obj()
        assert obj.attr == "args some_class2"
        assert obj.create_readonly_param() == ' readonly'
        obj = self.get_obj("new_args some_class2", attr3=False)
        assert obj.attr == "new_args some_class2"
        assert obj.create_readonly_param() == ''

    def test_implementation_control(self):
        pass
```

При запуске тестов:
```python
pytest your_module/your_test.py
```
будет выдано предупреждение(если все остальные тесты пройдут успешно):
```python
================================================================= warnings summary =================================================================
your_module/your_test.py::TestSomeClass2::test_create_readonly_param
  DeprecationWarning: 
  Checking class 'SomeClass2'. Testing generated a warning:
  Method <test_availability_control> has no implementation in class 'TestSomeClass2'
    Class defined at your_module/your_test.py:line number


your_module/your_test.py::TestSomeClass2::test_create_readonly_param
  DeprecationWarning: 
  Method <test_implementation_control> does not contain 'assert' in class 'TestSomeClass2'
    Class defined at your_module/your_test.py:line number


-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================================================== some passed, 2 warnings in 0.05s ==========================================================



```
