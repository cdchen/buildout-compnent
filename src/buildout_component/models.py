# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
from collections import OrderedDict, Mapping


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


RESULT_OPTION_NAME_SEPARATOR = '.'


class Result(Mapping):

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
        if RESULT_OPTION_NAME_SEPARATOR in key:
            return key
        return '{manifest}{separator}{key}'.format(
            manifest=manifest.id if isinstance(manifest, Manifest) else manifest,
            separator=RESULT_OPTION_NAME_SEPARATOR,
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
            if RESULT_OPTION_NAME_SEPARATOR in key:
                manifest, option_name = key.split(RESULT_OPTION_NAME_SEPARATOR)
            else:
                manifest, option_name = "", key
            contexts = out.get(manifest, None)
            if contexts is None:
                contexts = OrderedDict()
                out[manifest] = contexts

            contexts[option_name] = value
        return out
