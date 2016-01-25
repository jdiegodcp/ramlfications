import pytest
from ramlfications.nodelist import NodeList
from ramlfications import errors


class Person(object):
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


class DictionaryPerson(dict):
    pass


def test_nodelist():
    musk = Person(first_name='Elon', last_name='Musk')
    torvalds = Person(first_name='Linus', last_name='Torvalds')
    svensson = Person(first_name='Linus', last_name='Svensson')
    persons = NodeList([musk, torvalds, svensson])
    linuses = persons.filter_by(first_name='Linus')

    assert persons.first() is musk
    assert len(linuses) == 2
    assert linuses.filter_by(last_name='Svensson').one() == svensson
    assert linuses.first() == torvalds
    assert (
        linuses.filter_by(first_name='Linus').filter_by(last_name='Torvalds')
        .one() ==
        linuses.filter_by(first_name='Linus', last_name='Torvalds').one()
    )

    with pytest.raises(errors.InvalidNodeListFilterKey):
        persons.filter_by(middle_name='1337')

    with pytest.raises(errors.MultipleNodesFound):
        linuses.one()

    with pytest.raises(errors.NoNodeFound):
        linuses.filter_by(first_name='Guido').one()

    assert linuses.filter_by(first_name='Guido').first() is None


def test_nodelist_dicts():
    musk = DictionaryPerson(first_name='Elon', last_name='Musk')
    torvalds = DictionaryPerson(first_name='Linus', last_name='Torvalds')
    svensson = DictionaryPerson(first_name='Linus', last_name='Svensson')
    persons = NodeList([musk, torvalds, svensson])
    linuses = persons.filter_by(first_name='Linus')

    assert persons.first() is musk
    assert len(linuses) == 2
    assert linuses.filter_by(last_name='Svensson').one() == svensson
    assert linuses.first() == torvalds
    assert (
        linuses.filter_by(first_name='Linus').filter_by(last_name='Torvalds')
        .one() ==
        linuses.filter_by(first_name='Linus', last_name='Torvalds').one()
    )

    with pytest.raises(errors.InvalidNodeListFilterKey):
        persons.filter_by(middle_name='1337')

    with pytest.raises(errors.MultipleNodesFound):
        linuses.one()

    with pytest.raises(errors.NoNodeFound):
        linuses.filter_by(first_name='Guido').one()

    assert linuses.filter_by(first_name='Guido').first() is None
