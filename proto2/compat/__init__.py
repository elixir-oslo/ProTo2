import types

unicode = str


class Dict2(dict):
    def has_key(self, key):
        return key in self


def patch_dict(that):
#    def has_key(this, key):
#        return key in this
    that.has_key = types.MethodType(Dict2.has_key, that)
    #that.has_key = Dict2.has_key
    #setattr(that.__class__, 'has_key', has_key)
    return that
