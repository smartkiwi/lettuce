# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from optparse import make_option
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.test.utils import setup_test_environment
from django.test.utils import teardown_test_environment

from lettuce import Runner
from lettuce import registry

from lettuce.django import server
from lettuce.django import harvest_lettuces

class Command(NoArgsCommand):
    help = u'Run lettuce tests within each django app'

    option_list = NoArgsCommand.option_list[1:] + (
        make_option('-v', '--verbosity', action='store', dest='verbosity', default='4',
            type='choice', choices=['0', '3', '4'],
            help='Verbosity level; 0=no output, 3=colorless output, 4=normal output (colorful)'),
        make_option('-a', '--apps', action='store', dest='apps', default='',
            help='Run ONLY the django apps that are listed here. Comma separated'),
        make_option('-A', '--avoid-apps', action='store', dest='avoid_apps', default='',
            help='AVOID running the django apps that are listed here. Comma separated'),
        make_option('-S', '--no-server', action='store_true', dest='no_server', default=False,
            help="will not run django's builtin HTTP server"),
        make_option('-s', '--scenarios', action='store', dest='scenarios', default=None,
            help='Comma separated list of scenarios to run'),
    )
    def stopserver(self, failed=False):
        raise SystemExit(int(failed))

    def handle_noargs(self, **options):
        settings.DEBUG = False
        setup_test_environment()

        verbosity = int(options.get('verbosity', 4))
        apps_to_run = tuple(options.get('apps', '').split(","))
        apps_to_avoid = tuple(options.get('avoid_apps', '').split(","))

        run_server = not options.get('no_server', False)

        if run_server:
            server.start()

        failed = False
        try:
            for path in harvest_lettuces(apps_to_run, apps_to_avoid):
                registry.clear()
                result = Runner(path, options.get('scenarios'), verbosity).run()

                if not result or result.steps != result.steps_passed:
                    failed = True

        except Exception, e:
            import traceback
            traceback.print_exc(e)

        finally:
            server.stop(failed)
            teardown_test_environment()
