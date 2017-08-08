# fstmapping

A Pythonic interface for finite state transducers.

Requres [Pynini](http://www.openfst.org/twiki/bin/view/GRM/Pynini), which itself requires [OpenFst](http://openfst.org), [re2](http://github.com/google/re2), Python 2.7, and a C++ 11 compiler to build. 

An FstMapping is an immutable Python mapping that has strings as its keys and values and is
backed by a finite state transducer. 

```python
>>> m = FstMapping({"a": "b"})
>>> m["a"]
"b"
```

## Construction

FstMappings can be constructed directly from Pynini transducers, as well as from dictionaries or from 
any combination of arguments that can be passed to the `dict()` constructor.

```python
>>> import pynini
>>> m2 = FstMapping(pynini.transducer("a", "b").closure())
>>> m2["aaa"]
"bbb"
>>> m3 = FstMapping({"a": "c", "b": "c"})
>>> m3["a"]
"c"
>>> m4 = FstMapping(a="c", b="d")
>>> m3 == m4
True
```

## Reversible, composable, concatenable, intersectable...

Unlike regular dictionaries, they are bidirectional. The inverse of a FstMapping can be accessed using
the `.inv` property or the `~` operator (the same conventions used in
[bidict](https://bidict.readthedocs.io/en/latest/basic-usage.html)).

```python
>>> m.inv["b"]
"a"
>>> (~m)["b"]
"a"
>>> (~m)["a"]
KeyError
>>> ~~m == m
True
```

Other common FST operators are supported as well: `*` for composition, `+` for concatenation, `|` for union, and `&` for intersection.

```python
>>> n = FstMapping({"b": "c"})
>>> (m*n)["a"]
"c"
>>> (m+n)["ab"]
"bc"
>>> (m|n)["a"]
"b"
>>> (m|n)["b"]
"c"
```

Note that composition follows the convention that `(m*n)[k] == n[m[k]]` --- the *first* FstMapping given is the *innermost*. 
This convention is used in other FST libraries (e.g. Pynini, XFST, foma), and makes sense if `m` and `n` are thought of as sound 
changes, rewrite rules, or other transformations: `m*n` can be read in chronological order as "first apply `m`, then apply `n`." 
But it differs from the math convention where `f ∘ g(x) == f(g(x))`, or the Haskell convention where `(f . g) x == f (g x)`,
both readable as "first apply `g`, then apply `f`."

## One-to-many

Unlike regular dictionaries, FstMappings can be one-to-many. When a key is mapped to many values, the values are returned as a set.

```python
>>> m3 = FstMapping({"a": "c", "b": "c"})
>>> (~m3)["c"] == {"a", "b"}
True
```

Sets can also be used as keys. `m[{a,b,...,z}]` is syntactic sugar for `set(m[a])+set(m[b])+...+set(m[z])`. This gives the 
convenient properties that any value in `m` can serve as a key for `~m` and that `~m*m` maps every value in `m.values()` to itself. 
It also preserves the identity `(m*n)[a]==n[m[a]]`.

```python
>>> m3[{"a", "b"}]
"c"
>>> (~m3*m3)["c"]
"c"
```

`len(m)` returns the number of individual (non-set) keys in `m`, and `m.keys()` returns an iterator over the individual
(non-set) keys. This means that `len(m)` is equal to `len(m.keys())` but may not 
be equal to `len(m.values())`, that `len(m)` and `len(~m)` may not be equal, and that if `s` is a set then
`m[s]` is well-defined even though `s not in m.keys()`. 

(There is some Pythonic precedent for the last behavior
in slice objects: if `l` is an ordinary Python list and `s` is a slice, then `l[s]` is well-defined even though 
`s not in range(len(l))`).

## Potentially infinite

FstMappings can be based on a cyclic FST. This means that, unlike dictionaries, they can support mappings that take
a (theoretically) infinite number of keys, or return a (theoretically) infinite number of different values, or both. 
For instance, this transducer maps a string of `a`s of any length to a string of `b`s of equal length.

```python
>>> m2 = FstMapping(pynini.transducer("a", "b").closure())
>>> m2["aaaaa"]
"bbbbb"
>>> m2["a" * 100000]
"bbb ... b"
```

If `m` is cyclic on its key side, `len(m)`, `m.keys()`, `m.values()`, `m.items()`, and `for k in m` raise errors. If `m` is cyclic on its value
side and maps `k` to an infinite number of values, then `m[k]` and `m.get(k)` also raise errors.

A FstMapping created using the `limit()` method shows a different behavior. If `m = FstMapping( ... ).limit(n)` then 
`len(m)` is `n`; `len(m[k])` is at most `n` for any `k`; and `m.keys()`, `m.values()`, and `m.items()` yield at most `n` items
before stopping. There is no guarantee that `m.keys()`, `m.values()`, and `m.items()` on a limited FstMapping will yield 
*corresponding* keys and values: there may be some `k` in `m.keys()` such that `m[k]` is *not* in `m.values()`.

## Goals

* Python 2/3 support
* FstSet class for infinite set support, so that `m[k]` can be well-defined even if `k*m` is cyclic on the output side
* Priority union and priority composition operators (`/` and `%`?) for rule-based linguistic applications
* Methods for taking closure etc without calling on Pynini functions
* Automagic handling of sigmas in rewrite rules
* Mutability?
* Support for more FST libraries?
* Conversion between FstSets and re2 regexes?
