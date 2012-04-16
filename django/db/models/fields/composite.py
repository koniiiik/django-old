from . import Field
from django.utils.namedtuplecompat import namedtuple
from django.db.models import signals

class VirtualField(Field):
    """
    Base class for field types with no direct database representation.
    """
    def db_type(self, connection):
        return None

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        self.model = cls
        cls._meta.add_virtual_field(self)

    def get_attname_column(self):
        return self.get_attname(), None

class CompositeField(VirtualField):
    """
    Virtual field type enclosing several atomic fields into one.
    """
    def __init__(self, *fields, **kwargs):
        self.fields = fields
        super(CompositeField, self).__init__(**kwargs)

    def contribute_to_class(self, cls, name):
        super(CompositeField, self).contribute_to_class(cls, name)

        # We can process the fields only after they've been added to the
        # model class.
        def process_enclosed_fields(sender, **kwargs):
            nt_name = "%s_%s" % (cls.__name__, name)
            nt_fields = " ".join(f.name for f in self.fields)
            self.nt = namedtuple(nt_name, nt_fields)
            setattr(cls, name, self)
        signals.class_prepared.connect(process_enclosed_fields,
                                       sender=cls, weak=False)

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError("%s can only be retrieved via instance."
                                 % self.name)
        return self.nt._make(getattr(instance, f.name, None) for f in self.fields)

    def __set__(self, instance, value):
        for f, val in zip(self.nt._fields, value):
            setattr(instance, f, val)
