# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
from collections import OrderedDict, MutableMapping, Mapping

from buildout_component.errors import ImmutableValueError


class SimpleMapping(MutableMapping):
    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        self._data = OrderedDict(*args, **kwargs)

    def __delattr__(self, item):
        if item == 'data':
            raise ImmutableValueError()
        super().__delattr__(item)

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)

    def __delitem__(self, key):
        self._data.__delitem__(key)

    def __getitem__(self, item):
        return self._data.__getitem__(item)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        items = ['{key}={value}'.format(
            key=k, value=repr(v)
        ) for k, v in self.items()]
        return '{class_name}({items})'.format(
            class_name=self.__class__.__name__,
            items=', '.join(items)
        )


class ImmutableSimpleMapping(Mapping):
    def __setitem__(self, key, value):
        raise ImmutableValueError("The `{attr}` is immutable.".format(attr=key))

    def __delitem__(self, key):
        raise ImmutableValueError("The `{attr}` is immutable.".format(attr=key))
