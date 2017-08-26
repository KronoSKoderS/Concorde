import ctypes

from collections import OrderedDict

_no_type = object()


def typed_property(name, expected_type):
    """
    Simple function used to ensure a specific type for a property defined within a 
    class. 
    """
    storage_name = '_internal_' + name

    @property
    def prop(self):
        return getattr(self, storage_name)

    @prop.setter
    def prop(self, value):
        if not isinstance(value, expected_type):
            raise TypeError("{v} must be of type {t}".format(v=value, t=expected_type))
        setattr(self, storage_name, value)

    return prop


def _field_property(field_name, field):
    """
    Simple function used to allow for setting fields directly, and returning the class
    of the fields. 
    """
    @property
    def prop(self):
        return field

    @prop.setter
    def prop(self, value):
        # if we're the same field type, then we need to copy over the internal value
        if isinstance(value, type(field)):
            setattr(field, '_val', value._val)

        else:
            # Ensuring the type if it's set
            if field._type is not _no_type and not isinstance(value, field._type):
                raise TypeError("{v} must be of type {t1} or {t2}".format(v=value, t1=field._type, t2=type(field)))

            # Sets the internal value of the field
            setattr(field, '_val', value)

    return prop


class Field():
    """
    A Super class that all other fields inherit from.  When creating a new field, the
    following is required:

    1. Add to _acceptable_params for any new keyword arguments
    3. define _c_type
    4. define _type
    """

    _bit_len = typed_property('bit_len', int)
    _num_words = typed_property('num_words', int)
    _acceptable_params = set(['bit_len', 'num_words'])
    _c_type = None
    _type = _no_type
    _val = None

    def __init__(self, **kwargs):
        for k, v, in kwargs.items():
            if k not in self._acceptable_params:
                raise KeyError("`{k}` is not an accepted parameter for {cls}".format(k=k, cls=self.__class__))

        self._bit_len = kwargs.get('bit_len', 16)
        self._num_words = kwargs.get('num_words', 1)

    def __eq__(self, other):
        if isinstance(other, Field):
            return self._val == other._val
        return self._val == other

    def __lt__(self, other):
        if isinstance(other, Field):
            return self._val < other._val
        return self._val < other

    def __gt__(self, other):
        if isinstance(other, Field):
            return self._val > other._val
        return self._val > other

    def __ne__(self, other):
        return not self == other

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other < self

    def __repr__(self):
        return repr(self._val)

    def __str__(self):
        return str(self._val)


class IntField(Field):
    _unsigned = typed_property('unsigned', bool)
    _little_endian = typed_property('little_endian', bool)
    _type = int

    def __init__(self, **kwargs):
        self._acceptable_params.update(['little_endian', 'unsigned', 'initial_value'])
        super(IntField, self).__init__(**kwargs)

        self._little_endian = kwargs.get('little_endian', False)
        self._unsigned = kwargs.get('unsigned', False)
        if self._unsigned:
            self._c_type = ctypes.c_uint64
        else:
            self._c_type = ctypes.c_int64

        self._val = kwargs.get('initial_value', 0)


class ReservedField(Field):
    pass


class EncapsulatedPacketField(Field):
    def __init__(self, packet, **kwargs):
        pass


class _MetaPacket(type):
    def __new__(cls, clsname, bases, clsdict):
        d = dict(clsdict)
        
        order = []
        fields = []

        # for each 'Field' type we're gonna save the order and prep for the c struct
        for name, value in clsdict.items():
            # Encapsulated Packet are different.  They're already created packets.  
            if isinstance(value, _MetaPacket):
                value._type = value
                fields.append(('_' + name, value._c_struct))
                order.append(name)
                d[name] = _field_property(name, value)

            elif isinstance(value, Field):
                if value._num_words > 1:
                    value._type = list

                    # arrays will need to have a custom class underneath
                    class _field(ctypes.Structure):
                        _fields_ = [('value', value._c_type, value._bit_len)]

                    fields.append(('_' + name, _field * value._num_words))
                else:
                    fields.append(('_' + name, value._c_type, value._bit_len))

                order.append(name)
                d[name] = _field_property(name, value)

        # Here we save the order
        d['_fields_order'] = order

        # Here we save the structure
        class c_struct(ctypes.Structure):
            pass
        
        c_struct._fields_ = fields
        d['_c_struct'] = c_struct

        return type.__new__(cls, clsname, bases, d)

    @classmethod
    def __prepare__(metacls, clsname, bases, **kwargs):
        return OrderedDict()


class Packet(metaclass=_MetaPacket):
    
    def pack(self):
        c_pkt = self._c_struct()
        for f_name in self._fields_order:
            setattr(c_pkt, "_" + f_name, getattr(self, f_name)._val)

        return ctypes.string_at(ctypes.byref(c_pkt), ctypes.sizeof(c_pkt))

    @classmethod
    def unpack(cls, buf):
        cstring = ctypes.create_string_buffer(buf)
        c_pkt = ctypes.cast(ctypes.pointer(cstring), ctypes.POINTER(cls._c_struct)).contents
        pkt = cls()
        for f_name in cls._fields_order:
            setattr(pkt, f_name, getattr(c_pkt, "_" + f_name))

        return pkt
