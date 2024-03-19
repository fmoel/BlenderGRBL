# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Frank Moelendoerp

import os, json, bpy

def get_settings_path():
  user_path = bpy.utils.user_resource('CONFIG')
  return os.path.join(user_path, "grbl_settings.json")

class GlobalStorage(dict):
  _instance = None
  _filename = get_settings_path()
  keys_to_save = []

  def __init__():
    raise RuntimeError('Call instance() instead')

  @classmethod
  def instance(cls):
    if cls._instance is None:
      cls._instance = cls.__new__(cls)
    return cls._instance

  def restoreObject(self, obj):
    objectKeys = [a for a in dir(obj) if not a.startswith('_') and not callable(getattr(obj, a))]
    for key in self.keys():
      if key in objectKeys and key in self.keys_to_save:
        try:
          setattr(obj, key, self[key])
        except:
          pass # bpy maybe restricted at that moment (relevant for setters using ops)

  def saveObject(self, obj):
    objectKeys = [a for a in dir(obj) if not a.startswith('_') and not callable(getattr(obj, a))]
    for key in objectKeys:
      var = getattr(obj, key)
      if type(var) in [str, int, float, bool] and key in self.keys_to_save:
        self[key] = getattr(obj, key)

  def save(self):
    copy = {}
    for key in self.keys_to_save:
      copy[key] = self[key]
    with open(self._filename, "w+") as settings_file:
      json_string = json.dumps(copy)
      settings_file.write(json_string)

  def load(self):
    if os.path.exists(self._filename):
      with open(self._filename, "r+") as file:
        dict = json.load(file)
        for key in dict.keys():
          self[key] = dict[key]

  def set(self, name, val):
    self[name] = val
