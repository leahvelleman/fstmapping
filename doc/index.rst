.. fsmcontainers documentation master file, created by
   sphinx-quickstart on Tue Sep  5 18:13:01 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

fsmcontainers
=============

.. module:: fsmcontainers.fsmcontainers

.. testsetup:: *

   from fsmcontainers.fsmcontainers import fsa, fst
   import operator

This module provides two classes: 

   * :class:`fsa`, a finite-state acceptor that behaves like a Python set.
   * :class:`fst`, a finite-state transducer that behaves like a Python dict.

These offer a Pythonic interface for using finite-state linguistic
resources or hand-coding new ones.

    >>> from fsmcontainers import fst
    >>> piglatin = fst.read('piglatin.fst')
    >>> sentence = 'do you speak pig latin'
    >>> ' '.join([piglatin[w] for w in sentence.split()])
    'oday ouyay peaksay igpay atinlay'

    >>> sentence = 'Pig Latin, or "{pig latin}," is spoken by...'
    >>> sentence.format_map(piglatin)
    'Pig Latin, or "igpay atinlay," is spoken by...'

They are **not** meant to be high-performance replacements for
built-in :class:`set` and :class:`dict`.  For very large finite sets of strings
or mappings between strings, use `rust-fst <https://pypi.python.org/pypi/rust-fst>`_.  For high-performance
potentially-infinite sets of strings, you may be able to use regular
expressions, with :func:`re.match` as a test of set membership.

Both classes provide additional operations that are useful in computational
morphology, including cross product (:literal:`*`), composition (:literal:`@`),
and methods for constructing context-dependent rewrite rules.

Contents
--------

    * `Finite state acceptors`_
    * `Finite state transducers`_
    * `Shared operations`_ which apply to both acceptors and transducers


Finite state acceptors
----------------------

.. class:: fsa(iterable)
.. autoclass:: fsa

   Unlike sets, acceptors can have an infinite number of elements. But
   iterables passed to :class:`fsa` are eagerly evaluated, and so must be
   finite.  If, for instance, :class:`fsa` is passed a generator that never
   raises :literal:`StopIteration`, it will draw new values endlessly and never
   return.  To create a new infinite acceptor, use :meth:`plus` or :meth:`star`
   on a finite acceptor, or use other operations on an existing infinite
   acceptor. [#f1]_

   Instances of :class:`fsa` provide all the same operations as built-in
   Python :class:`set`, and compare equal to built-in sets with the same
   elements::

     >>> fsa('one', 'two', 'three') & {'three', 'four', 'five'}
     fsa('three')
     >>> fsa('one', 'two') == {'one', 'two'}
     True
     >>> fsa('one', 'two') > {'one'}
     True

   In addition, instances of :class:`fsa` provide all of the `shared
   operations`_, as well as the following operation:

   .. describe:: this * other
   .. automethod:: cross

Finite state transducers
------------------------

.. class:: fst(**kwargs)
.. class:: fst(mapping, **kwargs)
.. autoclass:: fst(iterable, **kwargs)

   In addition to the standard Python dictionary operations, fsts provide
   the following:

   .. automethod:: fst.query(iterable)
                   fst.query(string)

   .. automethod:: keyset

   .. automethod:: valueset


   .. describe:: this @ other ...
   .. automethod:: compose(*others)

   .. describe:: this @= other
      
      Update *this* in place by composing it with *other*.

      >>> s = fst({'input': 'intermediate'})
      >>> t = fst({'intermediate': 'output'})
      >>> s @= t
      >>> s['input']
      'output'

   .. describe:: this >> other ...
   .. describe:: ... other << this
   .. automethod:: priority_union(*others)

   .. describe:: this >>= other

      Update *this* in place by adding any mappings from *other* whose key is
      not already in *this*. This operation is an in-place version of rightward
      priority union, giving mappings in *this* priority over those in *other*.

      *Other* can also be an acceptor rather than a transducer. In that case,
      the outcome is:

          * All keys in *this* are mapped to their value in *this.*
          * All elements in *other* that aren't keys in *this* are mapped to
            themselves.

      >>> f = fst({"pig": "igpay", "latin": "atinlay", "words": "ordsway"})
      >>> g = fsa("normal", "english", "words")
      >>> f >>= g
      >>> f['pig']
      'igpay'
      >>> f['words']
      'ordsway'
      >>> f['english']
      'english'

   .. describe:: this <<= other

      Update *this* in place by adding all mappings from *other*, overwriting
      those whose key is already in *this*. This operation is an in-place
      version of leftward priority union, giving mappings in *other* priority
      over those in *this.

      *Other* can also be an acceptor rather than a transducer. In that case,
      the outcome is:

           * All elements in *other* are mapped to themselves.
           * All keys in *this* that aren't elements in *other* are mapped to
             their value in *this*.

      >>> f = fst({"pig": "igpay", "latin": "atinlay", "words": "ordsway"})
      >>> g = fsa("normal", "english", "words")
      >>> f <<= g
      >>> f['pig']
      'igpay'
      >>> f['words']
      'words'
      >>> f['english']
      'english'

   And they provide all of the `shared operations`_ documented in the following
   section:

Shared operations
-----------------

Both :class:`fsa`\ s and :class:`fst`\ s are instances of :class:`fsmcontainer`
and provide the following operations:

.. class:: fsmcontainer

   .. describe:: this + other ...
   .. automethod:: concatenate

   .. automethod:: star

   .. automethod:: plus

   .. describe:: len(a)
   .. automethod:: __len__

      Note that :func:`len` may be quite slow for large finite numbers of
      elements, though it is fast for infinite or small finite numbers. If
      you're getting the length of *a* to compare it to a small number,
      :meth:`len_compare` may be much faster.

   .. method:: len_compare(n, [operator=operator.eq])
   .. automethod:: len_compare(other, [operator=operator.eq])

      If *a* is a large finite acceptor, calculating :literal:`len(a)` can
      be very costly, but testing whether the number of elements is less than,
      equal to, or greater than a small integer *n* is fast. Use this method
      to avoid the costly full calculation of :literal:`len(a)` when *a* is
      not known to be small.

      .. doctest::

         >>> with open('/usr/share/dict/words') as f: # doctest: +SKIP
         ...     a = fsa(f.readlines())               # doctest: +SKIP
         >>> a.len_compare(0)                         # doctest: +SKIP
         False                                        # doctest: +SKIP
         >>> (a & {'supercalifragilisticexpialidocious'}).len_compare(0) # doctest: +SKIP
         True                                         # doctest: +SKIP
      
      Comparison with :literal:`float('inf')` can be used to determine if an
      acceptor is infinite or merely large.

      .. doctest::

         >>> a = fsa({'a'}).star()
         >>> a.len_compare(float('inf'))
         True
         >>> with open('/usr/share/dict/words') as f: # doctest: +SKIP
         ...     a = fsa(f.readlines())               # doctest: +SKIP
         >>> a.len_compare(float('inf'))              # doctest: +SKIP
         False                                        # doctest: +SKIP

      Similarly, if *this* may be large and *other* is known to be small, or
      vice versa, then :literal:`this.len_compare(other)` will be reliably
      fast, while :literal:`len(this) == len(other)` may be quite slow. 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. rubric:: Footnotes

.. [#f1] 

   It is easy to imagine infinite sets that cannot be constructed this way. But
   that is the point: the algorithms that make finite state acceptors efficient
   aren't able to handle arbitrary infinite sets. (Whereas we know that they
   *can* handle infinite sets that are constructed using Kleene star,
   intersection, union, subtraction, concatenation, and so on.) 
   
   Another way of putting this is that finite state acceptors have less
   computational power than Turing machines. That is good news in that it
   means we can check strings against them in small finite time. It is bad news
   in that it means there are sets whose membership they can't decide. In some
   domains that tradeoff is acceptable; in others it isn't.
