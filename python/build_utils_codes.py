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

def i_code (code3):
    return code3[0]

def o_code (code3):
    if len (code3) >= 2:
        return code3[1]
    else:
        return code3[0]

def tap_code (code3):
    if len (code3) >= 3:
        return code3[2]
    else:
        return code3[0]

def i_type (code3):
    return char_to_type[i_code (code3)]

def o_type (code3):
    return char_to_type[o_code (code3)]

def tap_type (code3):
    return char_to_type[tap_code (code3)]


char_to_type = {}
char_to_type['s'] = 'short'
char_to_type['i'] = 'int'
char_to_type['f'] = 'float'
char_to_type['c'] = 'gr_complex'
char_to_type['b'] = 'unsigned char'
