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

# The presence of this file turns this directory into a Python package

'''
This is the GNU Radio NORDIC module. Place your Python package
description here (python/__init__.py).
'''

# import swig generated symbols into the nordic namespace
try:
	# this might fail if the module is python-only
	from nordic_swig import *
        # import any pure python here
        from nordic_blocks import nordictap_transmitter, nordictap_printer
except ImportError:
	pass

# import any pure python here


#
