# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
from collections import OrderedDict, MutableMapping

from buildout_component.utils import SimpleMapping


class Manifest(object):
    id = ""
    title = ""
    section = ""
    options = []
    defaults = {}
    dependencies = []

    component_dir = ""
    manifest_path = ""
    hooks_dir_existed = False

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if not self.section:
            self.section = self.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '{class_name}(id={id}, title={title})'.format(
            class_name=self.__class__.__name__,
            id=self.id,
            title=self.title
        )


OPTION_NAME_SEPARATOR = '.'


class Options(SimpleMapping):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._group_by = OrderedDict()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        manifest, key = self.split_key(key)
        self._sync_group_by(manifest, key, value)

    def __delitem__(self, key):
        manifest, key = self.split_key(key)
        if manifest in self._group_by:
            del self._group_by[manifest][key]

    def _sync_group_by(self, manifest, key, value):
        if manifest not in self._group_by:
            self._group_by[manifest] = OrderedDict()
        self._group_by[manifest][key] = value

    def split_key(self, key):
        if OPTION_NAME_SEPARATOR in key:
            key = key.split(OPTION_NAME_SEPARATOR)
            return (key[0], ''.join(key[1:]))
        return ("", key)

    def get_key(self, manifest, key):
        return '{manifest}{separator}{key}'.format(
            manifest=manifest,
            separator=OPTION_NAME_SEPARATOR,
            key=key
        )

    def put(self, manifest, key, value):
        self._sync_group_by(manifest, key, value)
        key = self.get_key(manifest, key)
        self._data[key] = value

    @property
    def flat_dict(self):
        return OrderedDict(self._data)

    @property
    def group_by(self):
        return OrderedDict(self._group_by)


class Result(MutableMapping):

    def __init__(self, *args, **kwargs):
        # self.manifest = manifest.id if isinstance(manifest, Manifest) else manifest
        self._data = OrderedDict(*args, **kwargs)

    def __getitem__(self, key):
        return self._data.get(key)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        items = ['{key}={value}'.format(key=k, value=repr(v)) for k, v in self._data.items()]
        return '{class_name}({items})'.format(
            class_name=self.__class__.__name__,
            items=', '.join(items)
        )

    def get_key(self, manifest, key):
        if OPTION_NAME_SEPARATOR in key:
            return key
        return '{manifest}{separator}{key}'.format(
            manifest=manifest.id if isinstance(manifest, Manifest) else manifest,
            separator=OPTION_NAME_SEPARATOR,
            key=key,
        )

    def put(self, manifest, key, value):
        key = self.get_key(manifest, key)
        self._data[key] = value

    def empty(self, manifest, key):
        key = self.get_key(manifest, key)
        if key in self._data:
            del self._data[key]

    def put_all(self, manifest, results):
        for key, value in results.items():
            self.put(manifest, key, value)

    def group_by(self):
        out = OrderedDict()
        for key, value in self._data.items():
            if OPTION_NAME_SEPARATOR in key:
                manifest, option_name = key.split(OPTION_NAME_SEPARATOR)
            else:
                manifest, option_name = "", key
            contexts = out.get(manifest, None)
            if contexts is None:
                contexts = OrderedDict()
                out[manifest] = contexts

            contexts[option_name] = value
        return out
