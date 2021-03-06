Packet Fields
=============
:code:`calpack` comes with some built-in :code:`Field` classes that can be used right away.

:code:`IntField`
----------------
The :code:`IntField` is used to represent an integer.  In the backend, this field uses the 
:code:`ctypes.c_int` or :code:`ctypes.c_uint` depending on whether the field is configured as 
signed or not.  This is done by passing the :code:`signed` parameter to the :code:`IntField`::

    int_field = models.IntField(signed=True)

.. Note:: :code:`IntField` is unsigned as a default.
.. Warning:: If a signed value is set to an unsigned value (e.g any value less than 0) a 
    :code:`TypeError` will be raised.
.. Warning:: although the example above defines a field outside of a Packet, this **cannot** be 
    done in practice as each field within the packet **must** be a new instance of a Field.

There are also four other :code:`IntField` builtins that can be used to define a specific bit size:

    * :code:`IntField8` - wraps :code:`c_uint8` or :code:`c_int8`
    * :code:`IntField16` - wraps :code:`c_uint16` or :code:`c_int16`
    * :code:`IntField32` - wraps :code:`c_uint32` or :code:`c_int32`
    * :code:`IntField64` - wraps :code:`c_uint64` or :code:`c_int64`

Each one of these acts the same as :code:`IntField` with the only difference being their bit size. 
If a specific bit length is desired, passing the :code:`bit_len` parameter to the desired length::

    int_field = models.IntField(bit_len=8)

.. Note:: the default value for :code:`bit_len` is the size of the :code:`ctypes` data object.
.. Warning:: If bit_len is less than or equal 0 or greater than the size of the :code:`ctypes` data
    object a :code:`ValueError` will be raised.
.. Warning:: although the example above defines a field outside of a Packet, this **cannot** be 
    done in practice as each field within the packet **must** be a new instance of a Field.

Unused Bits
^^^^^^^^^^^
When creating packets with the :code:`IntField` and using the :code:`bit_len` param, certain 
circumstances may lead to unexpected behavior, specifically with the sizing of the packet.  This is
due to the way that :code:`ctypes` handles byte alignement.  For example::

    class simple(models.Packet):
        A = models.IntField8(bit_len=4)
        B = models.IntField8(bit_len=4)
        C = models.IntField8()

Will yield the following structure:

+---------------------------------------------------------------+
|                         bit locations                         |
+-------------------------------+-------------------------------+
|               Byte 0          |               Byte 1          |
+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+
| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| A | A | A | A | A | B | B | B | C | C | C | C | C | C | C | C |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

However, if not all bits of the Byte are not used, "spare" bits may be introduced::

    class simple(models.Packet):
        A = models.IntField8(bit_len=2)
        B = models.IntField8(bit_len=4)
        C = models.IntField8()

+---------------------------------------------------------------+
|                         bit locations                         |
+-------------------------------+-------------------------------+
|             Byte 0            |             Byte 1            |
+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+
| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| A | A | B | B | B | B |   |   | C | C | C | C | C | C | C | C |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

Notice that the last two bits of the first Byte are empty and won't be used!

It is recommended that if you use the :code:`bit_len` param for :code:`IntField`, to make sure your
field bits are byte aligned.

:code:`FloatField`
-------------------

The :code:`FloatField` is used to represent a floating point number.  Similar to the 
:code:`IntField` there are three fields that represent floating points:

    * :code:`FloatField` - wraps :code:`c_float`
    * :code:`DoubleField` - wraps :code:`c_double`
    * :code:`LongDoubleField` - wraps :code:`c_longdouble`

Each of these act the same, with the exception of their byte size.  

:code:`BoolField`
-----------------

The :code:`BoolField` is used to represent a :code:`bool` object in python.  This field wraps the
:code:`c_bool` data type in ctypes.  The size of this field is one byte even though only 
:code:`True` and :code:`False` are the acceptable values.  

:code:`FlagField`
-----------------

The :code:`FlagField` is used to represent a "flag" in the packet.  This is a single bit integer and
can only store a value of 1 or 0.  This field is similar to :code:`IntField8(bit_len=1)`.  

:code:`PacketField`
-------------------
The :code:`PacketField` is used to encapsulate another already defined packet.  The encapsulation 
of packets can be done multiple times as well::

    class Point(models.Packet):
        x = models.IntField(bit_len=8)
        y = models.IntField(bit_len=8)

    class Rectangle(models.Packet):
        top_left = models.PacketField(Point)
        top_right = models.PacketField(Point)
        bot_left = models.PacketField(Point)
        bot_right = models.PacketField(Point)

    class TwoRectangles(models.Packet):
        first_rect = models.PacketField(Rectangle)
        second_rect = models.PacketField(Rectangle)

:code:`ArrayField`
------------------

The :code:`ArrayField` is used to create an array of fields.  When creating the :code:`ArrayField`
two parameters must be passed:

    1. An instance of the Field to be used
    2. The size of the Array

Example::

    array_field = models.ArrayField(
        # Note that this is an **instance** of the IntField
        models.IntField(signed=True)
        12
    )

.. Note:: It's important to that the first argument is an **instance** of the Field and not the
    class
.. Warning:: although the example above defines a field outside of a Packet, this **cannot** be
    done in practice as each field within the packet **must** be a new instance of a Field. 

Interacting with the :code:`ArrayField` is similar to that of a python list where :code:`len` and 
individual member access can be done.  The Field instance for the first parameter of the 
:code:`ArrayField` can also be a :code:`PacketField`::

    class Point(models.Packet):
        x = models.IntField8()
        y = models.IntField8()

    class ArrayPacket(models.Packet):
        points = models.ArrayField(
            models.PacketField(Point),
            8
        )

    pkt = ArrayPacket()

    for i, point in enumerate(pkt.points):
        point.x = i
        point.y = len(pkt.points) - 1

    print([pkt.points[i].x, pkt.points[i].y for i in range(len(pkt.points))])
    [(0, 8), (1, 7), (2, 6), (3, 5), (4, 4), (5, 3), (6, 2), (7, 1)]

Accessing the members of an :code:`ArrayField` with a :code:`PacketField` as the field type will be
accessing instances of those packets::

    class ArrayPacket(models.Packet):
        points = array_field


    pkt = ArrayPacket()
    pkt.points[0].x = 100
    print(pkt.points[0].x)
    100

    print(pkt.points[0].y)
    0  # default value of IntField

ArrayField limitations and Workaround
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When using ArrayFields, there are limitations of what types of Fields can be used.  Any Field that
returns a tuple size greater than 2 from the :code:`create_field_c_tuple` method, cannot be used.  
An example Field is :code:`IntField` with the :code:`bit_len` set to a non byte aligned value.  
This is due to the complications of bit fields and arrays.

As a workaround to this, create a seperate Packet to be used as a PacketField within the Array.  
For Example::

    from calpack import models

    class simple_pkt(models.Packet):
        x = models.IntField8(bit_len=4)
        y = models.IntField8(bit_len=4)

    class adv_pkt(models.Packet):
        simple_pkts = models.ArrayField(models.PacketField(simple_pkt), 8)

.. note:: is is recommended that you use byte aligned fields within the PacketField otherwise some 
    bits might become unused.