import unicodedata
import pytest
import six
from hypothesis import given, assume, reject
from hypothesis.strategies import *
from hypothesis.stateful import RuleBasedStateMachine, Bundle, rule
from fsmcontainers import *
import random

usabletext = lambda: text(alphabet=characters(
    blacklist_characters=['\0', '\1'],
    blacklist_categories=['Cs']))

transducertext = lambda: lists(tuples(usabletext(), usabletext()))

kwargdicts = lambda: one_of(dictionaries(usabletext(), usabletext()),
                             dictionaries(usabletext(),
                                 tuples(usabletext(), usabletext())))

argdicts = lambda: one_of(kwargdicts(), 
                            dictionaries(
                                tuples(usabletext(), usabletext()),
                                tuples(usabletext(), usabletext())))

@composite
def fsts(draw):
    pairs = draw(transducertext())
    return fst(pairs)

def test_empty_constructor():
    a = fst()
    assert type(a) == fst

@given(kwargdicts())
def test_kwarg_constructor(kwargs):
    a = fst(**kwargs)
    assert type(a) == fst
    for k, v in kwargs.items():
        assert v in a.query({k})

@given(usabletext(), one_of(kwargdicts(), nothing()))
def test_constructor_fails_with_sequence_with_wrong_size_elements(s, kwargs):
    assume(s)
    with pytest.raises(ValueError):
        a = fst(s, **kwargs)
        assert a

@given(argdicts(), one_of(kwargdicts(), nothing()))
def test_mapping_constructor_with_dict_and_maybe_kwargs(d, kwargs):
    assume(d)
    if kwargs:
        assume(type(list(d.values())[0]) == type(list(kwargs.values())[0]))
        assume(type(list(d.keys())[0]) == type(list(kwargs.keys())[0]))
    a = fst(d, **kwargs)
    for k, v in d.items():
        assert v in a.query({k})
    for k, v in kwargs.items():
        assert v in a.query({k})

@given(lists(usabletext()), lists(usabletext()),
        one_of(dictionaries(usabletext(), usabletext()), nothing()))
def test_iterable_constructor_with_zip_and_maybe_kwargs(l1, l2, kwargs):
    a = fst(zip(l1, l2), **kwargs)
    for k, v in zip(l1, l2):
        assert v in a.query({k})
    for k, v in kwargs.items():
        assert v in a.query({k})

@given(dictionaries(usabletext(), lists(usabletext(), min_size=1)))
def test_query_retrieves_all_of_the_input_mappings_values(d):
    pairs = [(k, v) for k in d for v in d[k]]
    a = fst(pairs)
    for k in d:
        assert set(a.query({k})) == set(d[k])

@given(dictionaries(usabletext(), lists(usabletext(), min_size=1)))
def test_getitem_retrieves_one_of_the_input_mappings_values(d):
    pairs = [(k, v) for k in d for v in d[k]]
    a = fst(pairs)
    for k in d:
        assert a[k] in d[k]

@given(dictionaries(usabletext(), usabletext()),
        one_of(dictionaries(usabletext(), usabletext()), nothing()))
def test_len_matches_set_length_of_input_mappings_items(d, kwargs):
    a = fst(d, **kwargs)
    assert len(a) == len(set(d.items()) | set(kwargs.items()))

@given(lists(usabletext()), lists(usabletext()),
        one_of(dictionaries(usabletext(), usabletext()), nothing()))
def test_len_matches_set_length_of_input_iterable(l1, l2, kwargs):
    a = fst(zip(l1, l2), **kwargs)
    assert len(a) == len(set(zip(l1, l2)) | set(kwargs.items()))

@given(fsts())
def test_repr(d):
    assume(not "..." in repr(d))
    assert eval(repr(d)) == d

@given(fsts())
def test_keys_items_and_values_have_same_length(d):
    assert len(list(d.keys())) == len(list(d.values())) == len(list(d.items()))


