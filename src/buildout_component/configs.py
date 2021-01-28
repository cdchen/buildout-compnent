# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
from collections import UserList, OrderedDict

from buildout_component.models import Manifest
from buildout_component.utils import ContextMapping


class ConfigOptions(object):
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


class ConfigSectionOptions(ConfigOptions):
    section = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.operators = OrderedDict()
        self.operators.setdefault('eggs', '+=')


class ConfigSection(ContextMapping):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = ConfigSectionOptions()


class BaseBuildoutConfig(ContextMapping):

    def __getitem__(self, item):
        data = self.data
        if not item in data:
            section = ConfigSection()
            section.meta.section = item
            data[item] = section
        return data[item]

    # def __setitem__(self, key, value):
    #     if not isinstance(value, ConfigSection):
    #         value = ConfigSection(value)
    #     super().__setitem__(key, value)

    def __setitem__(self, key, value):
        if not isinstance(value, ConfigSection):
            value = ConfigSection(value)
        value.meta.section = key
        super().__setitem__(key, value)


class BuildoutConfig(BaseBuildoutConfig):
    def __init__(self, manifest, *args, **kwargs):
        assert manifest is not None, "The `manifest` argument is required."
        assert isinstance(manifest, Manifest), "The `manifest` argument must be instance of `Manifest`"

        self.manifest = manifest
        super().__init__(*args, **kwargs)

    def create_comment(self, value):
        return ConfigComment(value)
