"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import yaml
from datetime import datetime
import os
from contextlib import closing
import threading
import copy
from pathlib import Path


class PropertyManager:
    """
    Maintains a list of key-value pairs.
    """
    def __init__(self):
        self._properties = dict({})

    def is_key(self, key) -> bool:
        """
        Identifies if a key exists or not.

        :param key: The key of the value; should be a dot separated string of keys from root up the tree.
        :return: `True` if the key exists in the properties; `False` if the key doesn't exist in the properties.
        """
        if key is None or not key:
            return False
        find_dict = self._properties
        is_path, _, is_key = key.rpartition('.')
        if is_path:
            for part in is_path.split('.'):
                if isinstance(find_dict, dict):
                    find_dict = find_dict.get(part, {})
                else:
                    break
        if is_key in find_dict:
            return True
        return False

    def save(self, file_name: str):
        """
        Saves properties to a file.

        :param file_name: file in which to save properties
        """
        _time = str(datetime.now())
        self.set('meta', {'updated': _time})
        self._dump(self._properties, file_name)

    def load(self, config_file, replace=False) -> bool:
        """
        Loads the properties from the YAML configuration file; allows for multiple configuration.

        Files to be merged into the properties dictionary, or properties to be refreshed in real time.

        :param config_file: the path and filename of the YAML file
        :param replace: boolean value that identifies if the file is to be added or replaced
        :return: `True` if the file is found, opened, and loaded; `False` if an exception occurs

        """
        if config_file is None or not config_file or not isinstance(config_file, str):
            raise ValueError("The properties configuration file must be a valid str")

        _path = Path(config_file)
        if not _path.exists() or not _path.is_file():
            raise FileNotFoundError("Can't find the configuration file {}".format(_path))

        try:
            cfg_dict = self._load(_path)
        except (IOError, TypeError) as e:
            raise IOError(e)
        if replace:
            with threading.Lock():
                self._properties.clear()
                self._properties = cfg_dict
            return True
        for _key, _value in cfg_dict.items():
            # only replace sections that have changed
            if self.is_key(_key) and cfg_dict.get(_key) == self.get(_key):
                continue
            self.remove(_key)
            self.set(_key, _value)
        return True

    def get(self, key: str):
        """
        Gets a property value for the dot-separated key.

        :param key: the key of the value; should be a dot-separated string of keys from root up the tree

        :return:
            An object found in the key can be any structure found under that key.
            If the key is not found, `None` is returned.
            If the key is `None`, then the complete properties dictionary is returned.
            The full tree is returned under the requested key, be it a value, tuple, list, or dictionary.
        """
        if key is None or not key:
            return None

        rtn_val = self._properties
        for part in key.split('.'):
            if isinstance(rtn_val, dict):
                rtn_val = rtn_val.get(part)
                if rtn_val is None:
                    return None
            else:
                return None
        with threading.Lock():
            return copy.deepcopy(rtn_val)

    def set(self, key: str, value):
        """
        Sets a key-value pair. The value can be a union (str, dict, tuple, array).

       :param key: the key string
       :param value: the value of the key
       """
        if key is None or not key or not isinstance(key, str):
            raise ValueError("The key must be a valid str")
        keys = key.split('.')
        _prop_branch = self._properties
        _last_key = None
        _last_prop_branch = None
        # from base of the key work up to find where the section doesn't exist
        for _, k in list(enumerate(keys, start=0)):
            if k not in _prop_branch:
                break
            _last_prop_branch = _prop_branch
            _last_key = k
            _prop_branch = _prop_branch[k]
        tmp_dict = {}
        # now from the top of the key work back, creating the sections tree
        k = None
        for _, k in reversed(list(enumerate(keys, start=0))):
            if isinstance(value, dict):
                tmp_dict = {k: value}
            else:
                tmp_dict[k] = value
            if k is _last_key:
                break
            value = tmp_dict
        if not isinstance(value, dict):
            _last_prop_branch[k] = value
            return
        self._add_value(k, value, _prop_branch)
        return

    def _add_value(self, key, value, base):
        if key is None:
            return None
        for k, v in value.items():
            if isinstance(v, dict):
                if k in base:
                    base = base[k]
                    self._add_value(k, v, base)
                else:
                    with threading.Lock():
                        base.update({k: v})
            else:
                with threading.Lock():
                    base[k] = v
        return

    def remove(self, key) -> bool:
        """
        Removes a key-value from the in-memory configuration dictionary based on the key.

        :param key: the key of the key/value to be removed;
            should be a dot-separated string of keys from root up the tree

        :return: `True` if the key is removed; `False` if the key is not found
        """
        del_dict = self._properties
        del_path, _, del_key = key.rpartition('.')
        if del_path:
            for part in del_path.split('.'):
                if isinstance(del_dict, dict):
                    del_dict = del_dict.get(part)
                else:
                    return False
        if del_dict is None or del_key not in del_dict:
            return False
        with threading.Lock():
            del del_dict[del_key]
        return True

    def remove_all(self):
        with threading.Lock():
            meta = self._properties.get('meta')
            self._properties.clear()
            self.set('meta', meta)

    def get_all(self) -> dict:
        """
        Gets all the properties.

        :returns: a deep copy of the key-value pairs
        """
        with threading.Lock():
            return copy.deepcopy(self._properties)

    @staticmethod
    def join(*names, sep=None) -> str:
        """
        Used to create a name string or join paths by passing sep=os.path.sep.

        :param names: the names to join
        :param sep: the join separator; defaults to '.'
        :return: the names joined with the separator
        """
        _sep = sep if sep is not None else '.'
        return _sep.join(map(str, names))

    @staticmethod
    def _dump(data, config_file) -> None:
        _path, _file = os.path.split(config_file)
        if not os.path.exists(_path):
            os.makedirs(_path, exist_ok=True)
        _config_file = Path(config_file)
        with threading.Lock():
            # make sure the dump is clean
            try:
                with closing(open(_config_file, 'w')) as ymlfile:
                    yaml.safe_dump(data, ymlfile, default_flow_style=False)
            except IOError as e:
                raise IOError("The configuration file {} failed to open with: {}".format(config_file, e))
        # check the file was created
        if not _config_file.exists():
            raise IOError("Failed to save configconfiguration file {}. Check the disk is writable".format(config_file))
        return

    @staticmethod
    def _load(config_file) -> dict:
        config_file = Path(config_file)
        if not config_file.exists():
            raise FileNotFoundError("The configuration file {} does not exist".format(config_file))
        with threading.Lock():
            try:
                with closing(open(config_file, 'r')) as ymlfile:
                    rtn_dict = yaml.safe_load(ymlfile)
            except IOError as e:
                raise IOError("The configuration file {} failed to open with: {}".format(config_file, e))
            if not isinstance(rtn_dict, dict) or not rtn_dict:
                raise TypeError("The configuration file {} could not be loaded as a dict type".format(config_file))
            return rtn_dict
