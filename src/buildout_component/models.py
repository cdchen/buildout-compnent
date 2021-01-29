# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
import os
from collections import OrderedDict, UserList

from buildout_component.utils import SimpleMapping

OPTION_NAME_SEPARATOR = '.'


class Manifest(object):
    """
    The component's manifest data class.
    """
    id = ""
    title = ""
    section = ""
    options = []
    defaults = {}
    dependencies = []
    disabled = False

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

    def join(self, filename):
        return os.path.join(self.component_dir, filename)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'section': self.section,
            'options': self.options,
            'defaults': self.defaults,
            'disabled': self.disabled,
            'dependencies': self.dependencies,
        }


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


class ConfigOptions(object):
    """
    Config options class.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class ConfigItem(object):
    """
    The value of Config.
    """


class ConfigList(ConfigItem, UserList):
    pass


class ConfigComment(ConfigItem):
    def __init__(self, data):
        self.data = data

    def __hash__(self):
        return hash(self.data)

    def __str__(self):
        return '# {data} '.format(data=self.data)

    def __repr__(self):
        return '{class_name}(data={data})'.format(
            class_name=self.__class__.__name__,
            data=repr(self.data),
        )


class ConfigSection(SimpleMapping):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operators = OrderedDict()
        self.operators.setdefault('eggs', '+=')
        self.operators.setdefault('parts', '+=')


class BaseBuildoutConfig(SimpleMapping):

    def __getitem__(self, item):
        data = self._data
        if not item in data:
            section = ConfigSection()
            section.section = item
            data[item] = section
        return data[item]

    def __setitem__(self, key, value):
        if not isinstance(value, ConfigSection):
            value = ConfigSection(value)
        value.section = key
        super().__setitem__(key, value)


class BuildoutConfig(BaseBuildoutConfig):
    def __init__(self, manifest, *args, **kwargs):
        assert manifest is not None, "The `manifest` argument is required."
        assert isinstance(manifest, Manifest), "The `manifest` argument must be instance of `Manifest`"

        self.manifest = manifest
        super().__init__(*args, **kwargs)

    def create_comment(self, value):
        return ConfigComment(value)
