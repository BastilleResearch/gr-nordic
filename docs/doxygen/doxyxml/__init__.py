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
Python interface to contents of doxygen xml documentation.

Example use:
See the contents of the example folder for the C++ and
doxygen-generated xml used in this example.

>>> # Parse the doxygen docs.
>>> import os
>>> this_dir = os.path.dirname(globals()['__file__'])
>>> xml_path = this_dir + "/example/xml/"
>>> di = DoxyIndex(xml_path)

Get a list of all top-level objects.

>>> print([mem.name() for mem in di.members()])
[u'Aadvark', u'aadvarky_enough', u'main']

Get all functions.

>>> print([mem.name() for mem in di.in_category(DoxyFunction)])
[u'aadvarky_enough', u'main']

Check if an object is present.

>>> di.has_member(u'Aadvark')
True
>>> di.has_member(u'Fish')
False

Get an item by name and check its properties.

>>> aad = di.get_member(u'Aadvark')
>>> print(aad.brief_description)
Models the mammal Aadvark.
>>> print(aad.detailed_description)
Sadly the model is incomplete and cannot capture all aspects of an aadvark yet.
<BLANKLINE>
This line is uninformative and is only to test line breaks in the comments.
>>> [mem.name() for mem in aad.members()]
[u'aadvarkness', u'print', u'Aadvark', u'get_aadvarkness']
>>> aad.get_member(u'print').brief_description
u'Outputs the vital aadvark statistics.'

"""

from doxyindex import DoxyIndex, DoxyFunction, DoxyParam, DoxyClass, DoxyFile, DoxyNamespace, DoxyGroup, DoxyFriend, DoxyOther

def _test():
    import os
    this_dir = os.path.dirname(globals()['__file__'])
    xml_path = this_dir + "/example/xml/"
    di = DoxyIndex(xml_path)
    # Get the Aadvark class
    aad = di.get_member('Aadvark')
    aad.brief_description
    import doctest
    return doctest.testmod()

if __name__ == "__main__":
    _test()

