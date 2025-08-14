import pytest

def test_equal_or_not_equal():
    assert 3 == 3
    assert 1 != 3

def test_is_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('10', int)

def test_boolean():
    validate = True
    assert validate is True
    assert ('hello' == 'world') is False

def test_type():
    assert type('Hello' is str)
    assert type('Word' is not int)


def test_greather_and_less():
    assert  7 > 3
    assert 4 < 10

def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]

    assert 1 in num_list
    assert 7 not in num_list

    assert all(num_list)
    assert not any(any_list)

class Student:
    def __init__(self, name: str, last_name: str, major: str, year: int):
        self.name = name
        self.last_name = last_name
        self.major = major
        self.year = year

@pytest.fixture()
def default_student():
    return Student('John', 'Doe', 'Computer Science', 3)


def test_person_initialization(default_student):
    assert default_student.name == 'John', 'First name should be John'
    assert default_student.last_name == 'Doe', 'Last name should be Doe'
    assert default_student.major == 'Computer Science'
    assert default_student.year == 3
