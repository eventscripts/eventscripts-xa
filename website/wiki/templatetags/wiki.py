from django import template

register = template.Library()

class BAD: pass

class CallNode(template.Node):
    def __init__(self, func, args, kwargs, retvars):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.retvars = retvars

    def lookup_func(self, context):
        bits = self.func.split('.')
        last = bits.pop(-1)
        if bits:
            try:
                prefunc = template.Variable('.'.join(bits)).resolve(context)
            except template.VariableDoesNotExist:
                return BAD
        else:
            prefunc = context
        try:
            func = prefunc[last]
        except (TypeError, AttributeError, KeyError):
            try:
                func = getattr(prefunc, last)
            except (TypeError, AttributeError):
                try:
                    func = prefunc[int(last)]
                except (IndexError, ValueError, KeyError, TypeError):
                    return BAD
        if not callable(func):
            return BAD
        return func

    @staticmethod
    def resolve(var, context):
        if var[0] == var[-1] and var[0] in ('"',"'"):
            return var[1:-1]
        else:
            try:
                return template.Variable(var).resolve(context)
            except template.VariableDoesNotExist:
                return BAD

    def render(self, context):
        realfunc = self.lookup_func(context)
        if realfunc is BAD:
            return ''
        realargs = []
        for arg in self.args:
            real = self.resolve(arg, context)
            if real is BAD:
                return ''
            realargs.append(real)
        realkwargs = {}
        for key, value in self.kwargs.iteritems():
            real = self.resolve(value, context)
            if real is BAD:
                return ''
            realkwargs[key] = value
        try:
            retvalue = realfunc(*realargs, **realkwargs)
        except: # yes we really want to except ANY exception
            return ''
        if len(self.retvars) == 1:
            context[self.retvars[0]] = retvalue
        elif self.retvars:
            for var, val in zip(self.retvars, retvalue):
                context[var] = val
        else:
            return retvalue
        return ''

@register.tag
def call(parser, token):
    """
    Calls a function with arguments.
    
    {% call myobj.mymethod [arg1,arg2] [kwarg1=value1,kwarg2=value2] [as retvalue] %}
    """
    bits = token.split_contents()
    tagname = bits.pop(0)
    if not bits:
        raise template.TemplateSyntaxError, "call tag requires at least one argument"
    func = bits.pop(0)
    args = []
    kwargs = {}
    bit = None
    retvars = []
    while bits:
        bit = bits.pop(0)
        # Check if bit is a keyword argument
        if '=' in bit:
            k,v = bit.split('=', 1)
            kwargs[k] = v
        # Check if we're at the end of the argument list
        elif bit == 'as':
            retvars = bits
            break
        # Else append arguments list
        else:
            args.append(bit)
    # Return a call node
    return CallNode(func, args, kwargs, retvars)
