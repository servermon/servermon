# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
# Copyright © 2012 Faidon Liambotis
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
'''
Compat functions for old versions of Django
'''

from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION[:2] >= (1, 3):
    from django.shortcuts import render
else:
    # Copied from Django 1.3
    #
    # Copyright (c) Django Software Foundation and individual contributors.
    # All rights reserved.

    from django.template import loader, RequestContext
    from django.http import HttpResponse

    def render(request, *args, **kwargs):
        """
        Returns a HttpResponse whose content is filled with the result of calling
        django.template.loader.render_to_string() with the passed arguments.
        Uses a RequestContext by default.
        """
        httpresponse_kwargs = {
            'content_type': kwargs.pop('content_type', None),
            'status': kwargs.pop('status', None),
        }

        if 'context_instance' in kwargs:
            context_instance = kwargs.pop('context_instance')
            if kwargs.get('current_app', None):
                raise ValueError('If you provide a context_instance you must '
                                 'set its current_app before calling render()')
        else:
            current_app = kwargs.pop('current_app', None)
            context_instance = RequestContext(request, current_app=current_app)

        kwargs['context_instance'] = context_instance

        return HttpResponse(loader.render_to_string(*args, **kwargs),
                            **httpresponse_kwargs)

def monkey_patch_command_execute(name):
    """
    Monkey patches a django management command to give it an execute
    function that does not sys.exit(1) on CommandError. Bug was fixed in
    django 1.5 and hence this should only be used for less than 1.5 django
    version
    """
    from django.core import management
    from django.core.management.base import CommandError, BaseCommand
    import types
    # Populate the cache
    app_name = management.get_commands()[name]
    # Get the command
    if isinstance(app_name, BaseCommand):
        klass = app_name
    else:
        klass = management.load_command_class(app_name, name)

    def execute(self, *args, **options):
        """
        Try to execute this command, performing model validation if
        needed (as controlled by the attribute
        ``self.requires_model_validation``). If the command raises a
        ``CommandError``, intercept it and print it sensibly to
        stderr.
        """
        from django.utils.encoding import smart_str
        import sys
        show_traceback = options.get('traceback', False)

        try:
            self.stdout = options.get('stdout', sys.stdout)
            self.stderr = options.get('stderr', sys.stderr)
            if self.requires_model_validation:
                self.validate()
            output = self.handle(*args, **options)
            if output:
                if self.output_transaction:
                    # This needs to be imported here, because it relies on
                    # settings.
                    from django.db import connections, DEFAULT_DB_ALIAS
                    connection = connections[options.get('database', DEFAULT_DB_ALIAS)]
                    if connection.ops.start_transaction_sql():
                        self.stdout.write(self.style.SQL_KEYWORD(connection.ops.start_transaction_sql()) + '\n')
                self.stdout.write(output)
                if self.output_transaction:
                    self.stdout.write('\n' + self.style.SQL_KEYWORD("COMMIT;") + '\n')
        except CommandError, e:
            if show_traceback:
                traceback.print_exc()
            else:
                self.stderr.write(smart_str(self.style.ERROR('Error: %s\n' % e)))
    setattr(klass, 'execute', types.MethodType(execute, klass))
    # Finalize command manipulation
    management._commands[name] = klass

