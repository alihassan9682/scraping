from funtions import Person


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4


def test_hello(): 
    person = Person('Ali', '25')
    assert person.sayHi() == 'Hello, my name is Ali and I am 25 years old!'
