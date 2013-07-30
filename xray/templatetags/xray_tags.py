from string import ascii_lowercase

from django import template

register = template.Library()

letters = [l.upper() for l in ascii_lowercase]


@register.filter
def alphabet(index):
    return letters[index]


@register.filter
def cell_style(prct):
    if prct:
        prct = float(prct)
        color = (" color: hsla(200, 100%%, 0%%, %.2f);" %
                 ((prct / 100.0) + 0.5))
        background = ("background-color: hsla(200, 80%%, 50%%, %.2f);" %
                      (prct / 100.0))
        return background + color
    return ""


# the following is from: http://djangosnippets.org/snippets/2147/

class RangeNode(template.Node):
    def __init__(self, parser, range_args, context_name):
        self.template_parser = parser
        self.range_args = range_args
        self.context_name = context_name

    def render(self, context):

        resolved_ranges = []
        for arg in self.range_args:
            compiled_arg = self.template_parser.compile_filter(arg)
            resolved_ranges.append(compiled_arg.resolve(context,
                                                        ignore_failures=True))
        context[self.context_name] = range(*resolved_ranges)
        return ""


@register.tag
def mkrange(parser, token):
    """
    Accepts the same arguments as the 'range' builtin and creates
    a list containing the result of 'range'.

    Syntax:
        {% mkrange [start,] stop[, step] as context_name %}

    For example:
        {% mkrange 5 10 2 as some_range %}
        {% for i in some_range %}
          {{ i }}: Something I want to repeat\n
        {% endfor %}

    Produces:
        5: Something I want to repeat
        7: Something I want to repeat
        9: Something I want to repeat
    """

    tokens = token.split_contents()
    fnctl = tokens.pop(0)

    def error():
        raise template.TemplateSyntaxError,\
            ("%s accepts the syntax: "
             "{%% %s [start,] stop[, step] as context_name %%}, "
             "where 'start', 'stop' and 'step' must all "
             "be integers." % (fnctl, fnctl))

    range_args = []
    while True:
        if len(tokens) < 2:
            error()

        token = tokens.pop(0)

        if token == "as":
            break

        range_args.append(token)

    if len(tokens) != 1:
        error()

    context_name = tokens.pop()

    return RangeNode(parser, range_args, context_name)
