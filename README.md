# DinamicMiniControlTest #

Этот проект - не панацея, не замена coverage и ему подобным!

Базовый класс настроек для наследования основного класса.
Так же помогает создавать объект тестирования с различными атрибутами "на лету".

Классы:
```python
class SomeBaseClass:
    type: str = None
    
    def __init__(self, attr1: str = None, attr2: str = None, attr3: bool = False):
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

Тестирование:
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
    obj: Type[SomeBaseClass] = None
    attr1: str = "some_attr1"
    attr2: str = "some_attr2"
    attr3: bool = True
    attr4: bool = False

    class Meta:
        # attr4 будет проигнорирован при вызове объекта тестирования.
        exclude_for_set = ["attr4"]
    
    # Необязательный метод. Создан для удобства - добавляет подсказки при наборе self.get_obj() и "смотрит" за именами методов
    @wraps(obj.__class__.__init__)
    def get_obj(self, **kwargs) -> obj:
        return super().get_obj(**kwargs)
    
    # общие методы тестирования класса, когда от наличия аргументов или их значения результат не поменяется
    def test_init_obj(self):
        obj = self.get_obj()
        assert isinstance(obj.__class__, self.obj.__class__)
        assert obj.attr1 == "some_attr1"
        assert obj.attr2 == "some_attr2"
        assert obj.attr3 is True
        assert obj.create_obj == 'some_attr1 some_attr2'
        assert obj.attr5 == 'some_attr1 some_attr2'
        obj = self.get_obj(attr1="new_attr1")
        assert obj.create_obj == 'new_attr1 some_attr2'
        assert obj.attr5 == 'new_attr1 some_attr2'
        
        
class TestSomeClass(BaseClassTest):
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

    def test_create_readonly_param(self):
        # в разных классах результат может различаться в зависимости от аргумента в вызове объекта
        obj = self.get_obj()
        assert obj.create_readonly_param() == ' readonly'
        obj = self.get_obj(attr3=False)
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
================================================== warnings summary ==================================================
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
===================================== some passed, 2 warnings in 0.05s =====================================

```
