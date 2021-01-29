# -*- coding: utf-8 -*-
#
# Buildout Component
# 
# All rights reserved by Cd Chen.
#
import base64
import configparser
import importlib
import json
import os
import pickle
import re
import sys
from collections import OrderedDict
from datetime import datetime

import wrapt as wrapt

from buildout_component.contexts import Context
from buildout_component.models import Manifest, Options, ConfigList, ConfigSection as _ConfigSection, \
    BaseBuildoutConfig, BuildoutConfig

TERMINATOR = "\x1b[0m"
ERROR = "\x1b[1;31m [ERROR]: "
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;34m [INFO]: "
HINT = "\x1b[3;37m [HINT]: "
SUCCESS = "\x1b[1;32m [SUCCESS]: "

MANIFEST_NAME = "manifest.json"
COMPONENT_SECTION_NAME_IN_CONFIG = 'buildout_component'

HOOKS_DIR_NAME = "hooks"

HOOK_FILE_TEMPLATE = """# -*- coding: utf-8 -*-
#
# Buildout Component Option Hook
#


def collect_result(context):
    pass

"""


class BaseProxyObject(wrapt.ObjectProxy):
    _wrapped_class = None

    def __init__(self, wrapped):
        super().__init__(wrapped)


class ConfigSection(BaseProxyObject):
    _wrapped_class = _ConfigSection

    def _merge_with_key_value(self, key, another):
        my_value = self.get(key, None)
        if my_value is None:
            my_value = ConfigList()

        if isinstance(another, (tuple, list, ConfigList)):
            my_value.extend(another)
        else:
            my_value.append(another)
        self[key] = my_value

    def merge(self, another):
        if not isinstance(another, (tuple, list, dict, BuildoutConfig, ConfigSection)):
            return

        another = dict(another)

        all_keys = set(self.keys()) | set(another.keys())

        for key in self.keys():
            a_value = another.get(key, [])
            self._merge_with_key_value(key, a_value)
            all_keys.remove(key)

        for key in all_keys:
            a_value = another.get(key, [])
            self._merge_with_key_value(key, a_value)

    def _render_key(self, key, value):
        return key

    def _render_value(self, key, value):
        if isinstance(value, (tuple, list)):
            return [self._render_value(key, v) for v in value]

        return str(value).strip() if value is not None else ''

    def _render_operator(self, key, value):
        return self.operators.get(key, '=')

    def render(self, padding=4, template=''):
        items = ['[{section}]'.format(section=self.section)]

        padding = ' ' * padding
        template = template or '{key} {operator} {values}'
        value_separator = '\n{padding}'.format(padding=padding)

        for key, value in self.items():
            key = self._render_key(key, value)
            operator = self._render_operator(key, value)
            value = self._render_value(key, value)
            if isinstance(value, (tuple, list, ConfigList)):
                values = value
            elif isinstance(value, dict):
                values = list(value.items())
            else:
                values = [value]
            if len(values) > 1:
                values.insert(0, padding)
                value = value_separator.join(values)
            else:
                value = ''.join(values)
            items.append(template.format(
                key=key,
                operator=operator,
                values=value,
            ))
        return items


class FinalBuildoutConfig(BaseBuildoutConfig):

    def _merge_with_key_value(self, key, another):
        my_value = self.get(key, None)
        if my_value is None:
            my_value = ConfigSection()
        if not isinstance(my_value, ConfigSection):
            my_value = ConfigSection(another)

        my_value.merge(another)
        self[key] = my_value

    def merge(self, another):
        if not isinstance(another, (tuple, list, dict, BaseBuildoutConfig, ConfigSection)):
            return

        another = dict(another)

        all_keys = set(self.keys()) | set(another.keys())

        for key in self.keys():
            a_value = another.get(key, None)
            if a_value is not None:
                self._merge_with_key_value(key, a_value)
            all_keys.remove(key)

        for key in all_keys:
            a_value = another.get(key, None)
            if a_value is not None:
                self._merge_with_key_value(key, a_value)

    def _render_section(self, section, data, padding=4, wrapper_class=ConfigSection):
        lines = []
        if data is not None:
            data = wrapper_class(data)
            output = data.render(padding)
            if isinstance(output, (tuple, list)):
                lines.extend(output)
            else:
                lines.append(output)
        lines.append('\n')
        return lines

    def render(self, padding=4):
        lines = []

        buildout = self.pop('buildout', None)
        lines.extend(self._render_section('buildout', buildout, padding=padding))

        versions = self.pop('versions', None)
        lines.extend(self._render_section('versions', versions, padding=padding))

        buildout_component = self.pop('buildout_component', None)

        for section, data in self.items():
            lines.extend(self._render_section(section, data, padding=padding))

        lines.extend(self._render_section(COMPONENT_SECTION_NAME_IN_CONFIG, buildout_component, padding=padding))

        return '\n'.join(lines)


class Command(object):
    def __init__(self):
        try:
            import argparse
        except ImportError:
            sys.stderr.write("{level}{message}{terminator}\n".format(
                level=ERROR,
                message="This program require the `argparse` module, install it before run.",
                terminator=TERMINATOR
            ))
            sys.exit(1)

        common_parser = argparse.ArgumentParser(add_help=False)
        common_parser.add_argument(
            '-p',
            '--project-root',
            help='The project root directory. default=%(default)s',
            default=os.getcwd(),
        )
        common_parser.add_argument(
            '-c',
            '--components-dir',
            help='The component directory. default=%(default)s',
            default="buildout/components/",
        )
        common_parser.add_argument(
            '-o',
            '--output-file',
            help="The output file. default=%(default)s",
            default='buildout/components/component.cfg',
        )

        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers()

        # collect sub-command
        collect_parser = subparsers.add_parser(
            "collect",
            help="Collect all options of components.",
            parents=[common_parser]
        )
        collect_parser.add_argument(
            'defaults',
            help="The defaults.",
            nargs="*",
        )
        collect_parser.set_defaults(func=self.collect)

        # show-defaults subcommand
        show_defaults_parser = subparsers.add_parser(
            'show-defaults',
            help="Show all defaults.",
            parents=[common_parser],
        )
        show_defaults_parser.set_defaults(func=self.show_defaults)

        # create-component subcommand
        create_component_parser = subparsers.add_parser(
            'create',
            help="Create component materials.",
            parents=[common_parser],
        )
        create_component_parser.add_argument(
            '--id',
            help="The id of component."
        )
        create_component_parser.add_argument(
            '--name',
            help="The name of component.",
        )
        create_component_parser.add_argument(
            '--section',
            help="The section of component.",
        )
        create_component_parser.add_argument(
            '--dependencies',
            help="The dependencies components.",
            nargs="*"
        )
        create_component_parser.add_argument(
            '--disable-create-hooks',
            help="Disable create hook files.",
            action="store_true",
        )
        create_component_parser.add_argument(
            'option',
            help="The option names. format: <NAME>[=<VALUE>]",
            nargs="*",
        )
        create_component_parser.set_defaults(func=self.create_component)

        self.parser = parser

    def _scan_components(self):
        all_component_list = []
        all_component_dict = OrderedDict()

        for dir_name in os.listdir(self.options.components_dir):
            if not dir_name.isidentifier():
                continue
            dir_path = os.path.join(self.options.components_dir, dir_name)
            if not os.path.isdir(dir_path):
                continue
            manifest_path = os.path.join(dir_path, MANIFEST_NAME)
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as fp:
                    manifest = json.load(fp)
                    if not manifest:
                        continue
                    if not isinstance(manifest, dict):
                        continue

                    if not manifest.get('id', ''):
                        manifest['id'] = dir_name.lower().replace("-", '_')
                    manifest.update({
                        'component_dir': dir_name,
                        'manifest_path': manifest_path,
                    })
                    manifest = Manifest(**manifest)

                    manifest.hooks_dir_existed = os.path.exists(os.path.join(dir_path, HOOKS_DIR_NAME))

                    all_component_list.append(manifest)
                    all_component_dict[manifest.id] = manifest

        self.all_component_list = all_component_list
        self.all_component_dict = all_component_dict

    def _default_collect_result_handler(self, manifest, name):
        return manifest.defaults.get(name, None)

    def _collect_options(self, manifest):
        options = OrderedDict()
        module_name_prefix = self._get_component_python_module_name()

        for option_name in manifest.options:
            try:
                if manifest.hooks_dir_existed is False:
                    raise ImportError()

                module_name = '{module_name}.{component}.{hooks}.{option_name}'.format(
                    module_name=module_name_prefix,
                    hooks=HOOKS_DIR_NAME,
                    component=manifest.id,
                    option_name=option_name,
                )
                module = importlib.import_module(module_name)
                handler = getattr(module, 'collect_result', None)
                if handler:
                    result = handler(self.context)
                else:
                    raise ImportError()
            except ImportError:
                result = self._default_collect_result_handler(manifest, option_name)

            if not isinstance(result, dict):
                result = {option_name: result}

            options.update(result)
        return options

    def _collect_manifest(self, manifest):
        for dependency in manifest.dependencies:
            dependency = self.all_component_dict.get(dependency, None)
            if not dependency:
                continue
            self._collect_manifest(dependency)

        if manifest.id not in self.context.collected:
            self.context.manifest = manifest.id
            self.context.config = BuildoutConfig(manifest)
            self.context.defaults = self.defaults.group_by[manifest.id]

            options = self._collect_options(manifest)

            self.context.collected[manifest.id] = OrderedDict({
                'config': self.context.config,
                'options': options
            })

    def _get_component_python_module_name(self):
        return os.path.basename(os.path.abspath(self.options.components_dir))

    def _get_defaults(self):
        defaults = Options()

        for manifest_id, manifest in self.all_component_dict.items():
            for key, value in manifest.defaults.items():
                defaults.put(manifest_id, key, value)

        if os.path.exists(self.options.output_file):
            buildout_config = configparser.ConfigParser()
            buildout_config.read(self.options.output_file)
            if COMPONENT_SECTION_NAME_IN_CONFIG in buildout_config.sections():
                data = buildout_config[COMPONENT_SECTION_NAME_IN_CONFIG].get('options', '')
                if data:
                    try:
                        data = pickle.loads(base64.b64decode(data))
                        if data is not None:
                            defaults.update(data)
                    except Exception:
                        pass

        if hasattr(self.options, 'defaults'):
            reg = re.compile('(?P<key>[^\s=]+)=(?P<value>.*)')
            for item in list(self.options.defaults):
                match = reg.match(item)
                if not match:
                    continue
                key, value = match.group('key'), match.group('value')
                defaults[key] = value

        return defaults

    def collect(self):
        self.context = Context()

        self._scan_components()

        if not self.all_component_list:
            sys.exit(0)

        self.defaults = self._get_defaults()

        self.results = OrderedDict()

        python_sys_path = os.path.dirname(os.path.abspath(self.options.components_dir))
        if python_sys_path not in sys.path:
            sys.path.insert(0, python_sys_path)

        for manifest in self.all_component_list:
            self._collect_manifest(manifest)

        final_buildout_config = FinalBuildoutConfig()
        final_options = Options()

        for manifest_id, collected_data in self.context.collected.items():
            collected_config = collected_data.get('config')

            final_buildout_config.merge(collected_config)

            collected_options = collected_data.get('options', {})

            for key, value in collected_options.items():
                final_options.put(manifest_id, key, value)

        buildout_component = _ConfigSection(section=COMPONENT_SECTION_NAME_IN_CONFIG)
        buildout_component['options'] = base64.b64encode(pickle.dumps(final_options)).decode('utf-8')
        buildout_component['create_time'] = repr(str(datetime.utcnow()))

        final_buildout_config[COMPONENT_SECTION_NAME_IN_CONFIG] = buildout_component
        rendered_data = final_buildout_config.render()

        action = "Update" if os.path.exists(self.options.output_file) else "Create"
        with open(self.options.output_file, 'w') as fp:
            fp.write(rendered_data)

        print(SUCCESS + "{action} {output_file} success. ".format(
            action=action,
            output_file=self.options.output_file
        ) + TERMINATOR)

    def show_defaults(self):
        self._scan_components()
        self.defaults = self._get_defaults()
        for key, value in self.defaults.flat_dict.items():
            print("{key}={value}".format(key=key, value=repr(value)))

    def create_component(self):
        """

            --id
            --name
            --section
            --dependencies

            option

        :return:
        """

        try:
            _id = self.options.id
            while not _id:
                _id = input("Component ID: ").strip()
                component_dir = os.path.join(self.options.components_dir, _id)
                if os.path.exists(component_dir):
                    sys.stderr.write(WARNING + "Component directory is existed." + TERMINATOR + "\n")
                    _id = False

            _name = self.options.name
            if not _name:
                _name = input("Component Name: ").strip()

            section = input("Component section: [{section}] ".format(section=self.options.section or _id))
            if not section:
                section = _id

        except KeyboardInterrupt:
            sys.stderr.write("\n" + WARNING + "User break. " + TERMINATOR + "\n")
            sys.exit(1)

        component_dir = os.path.join(self.options.components_dir, _id)
        defaults = OrderedDict()
        options = []
        for option in self.options.option:
            option = option.strip().split('=')
            if len(option) == 1:
                name, value = option[0], None
            else:
                name, value = option[0], ''.join(option[1:])
            options.append(name)
            defaults[name] = value

        dependencies = self.options.dependencies

        manifest = Manifest()
        manifest.id = _id
        manifest.name = _name
        manifest.section = section
        manifest.options = options
        manifest.defaults = defaults
        manifest.dependencies = dependencies
        data = json.dumps(manifest.serialize(), indent=4)

        line = '-' * 60
        print("Manifest: ")
        print(line)
        print(data)
        print(line)
        ans = input("Sure ? [y/N] ")
        if ans.lower() != 'y':
            sys.stderr.write(WARNING + "Break." + TERMINATOR + "\n")
            sys.exit(1)
        os.makedirs(component_dir)
        with open(os.path.join(component_dir, MANIFEST_NAME), "w") as fp:
            fp.write(data)

        hooks_dir = os.path.join(component_dir, HOOKS_DIR_NAME)
        os.makedirs(hooks_dir)
        for option in options:
            with open(os.path.join(hooks_dir, '{option}.py'.format(option=option)), "w") as fp:
                fp.write(HOOK_FILE_TEMPLATE)

        print(SUCCESS + "Component create success." + TERMINATOR)

    def execute(self):
        self.options = self.parser.parse_args()

        if hasattr(self.options, 'func'):
            setup_path = lambda p: p if os.path.isabs(p) else os.path.join(self.options.project_root, p)

            self.options.components_dir = setup_path(self.options.components_dir)
            self.options.output_file = setup_path(self.options.output_file)

            self.options.func()
        else:
            self.parser.print_help()


def main():
    Command().execute()


if __name__ == '__main__':
    main()
