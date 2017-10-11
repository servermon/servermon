# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
# Copyright © 2012 Faidon Liambotis
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
'''
Compat functions for old versions of Django
'''


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

        try:
            self.stdout = options.get('stdout', sys.stdout)
            self.stderr = options.get('stderr', sys.stderr)
            if self.requires_model_validation:
                self.validate()
            output = self.handle(*args, **options)
            if output:
                # Since this is only used for error catching an actual body in
                # this is useless. Just pass
                pass
        except CommandError as e:
                self.stderr.write(smart_str(self.style.ERROR('Error: %s\n' % e)))
    setattr(klass, 'execute', types.MethodType(execute, klass))
    # Finalize command manipulation
    management._commands[name] = klass
