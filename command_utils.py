import os
import subprocess
import sys
from functools import wraps

import click
from click import MissingParameter, echo, secho
from click._compat import get_text_stderr

from click import HelpFormatter, wrap_text
from click._compat import term_len
from colorama import init
from termcolor import colored

init()
message_cyan = lambda x: colored(x, 'cyan', attrs=['blink'])
message_red = lambda x: colored(x, 'red', attrs=['blink'])


def write_usage(self, prog, args='', prefix='Usage: '):
    """Writes a usage line into the buffer.
    :param prog: the program name.
    :param args: whitespace separated list of arguments.
    :param prefix: the prefix for the first line.
    """
    usage_prefix = message_cyan('%*s%s ' % (self.current_indent, prefix, prog))
    text_width = self.width - self.current_indent

    if text_width >= (term_len(usage_prefix) + 20):
        # The arguments will fit to the right of the prefix.
        indent = ' ' * term_len(usage_prefix)
        self.write(wrap_text(args, text_width,
                             initial_indent=usage_prefix,
                             subsequent_indent=indent))
    else:
        # The prefix is too long, put the arguments on the next line.
        self.write(usage_prefix)
        self.write('\n')
        indent = ' ' * (max(self.current_indent, term_len(prefix)) + 4)
        self.write(wrap_text(args, text_width,
                             initial_indent=indent,
                             subsequent_indent=indent))


def write_text(self, text):
    """Writes re-indented text into the buffer.  This rewraps and
          preserves paragraphs.
    """
    self.write(text)
    self.write('\n')


def color(self, message):
    message = message_cyan(message)
    self.buffer.append('%*s%s:\n' % (self.current_indent, '', message))


HelpFormatter.write_heading = color
HelpFormatter.write_usage = write_usage
HelpFormatter.write_text = write_text

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def empty_helper_message(f):
    @wraps(f)
    @click.pass_context
    def helper(ctx, *args, **kwargs):
        if is_help(ctx):
            click.echo(ctx.get_help())
            if not is_help_arg(ctx):
                sys.exit(0)
        return f(ctx, *args, **kwargs)

    return helper


class CustomMissingException(MissingParameter):
    def __init__(self, message=None, ctx=None, param=None,
                 param_hint=None, param_type=None):
        MissingParameter.__init__(self, message, ctx, param, param_hint)
        self.param_type = param_type

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()
        if self.ctx:
            color = self.ctx.color
            echo(self.ctx.get_help(), file=file, color=color)
        secho('Error: %s' % self.format_message(), file=file, fg="red")

def require_param(ctx, param, value):
    if not is_help(ctx) and not value:
        raise CustomMissingException(ctx=ctx, param=param)
    return value

def title_header(art=""):
    """
    Decorator: Append to a function's docstring.
    """

    def _decorator(func):
        ascii_text = message_red(art.lstrip().rstrip())

        func.__doc__ = ascii_text
        return func

    return _decorator


class UserException(click.ClickException):
    exit_code = 1

import click
import ast

class PythonLiteralOption(click.Option):

    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)