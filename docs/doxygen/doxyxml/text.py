'''
  Copyright (C) 2016 Bastille Networks

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

"""
Utilities for extracting text from generated classes.
"""

def is_string(txt):
    if isinstance(txt, str):
        return True
    try:
        if isinstance(txt, unicode):
            return True
    except NameError:
        pass
    return False

def description(obj):
    if obj is None:
        return None
    return description_bit(obj).strip()

def description_bit(obj):
    if hasattr(obj, 'content'):
        contents = [description_bit(item) for item in obj.content]
        result = ''.join(contents)
    elif hasattr(obj, 'content_'):
        contents = [description_bit(item) for item in obj.content_]
        result = ''.join(contents)
    elif hasattr(obj, 'value'):
        result = description_bit(obj.value)
    elif is_string(obj):
        return obj
    else:
        raise StandardError('Expecting a string or something with content, content_ or value attribute')
    # If this bit is a paragraph then add one some line breaks.
    if hasattr(obj, 'name') and obj.name == 'para':
        result += "\n\n"
    return result
