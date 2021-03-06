# -*- coding: iso-8859-1 -*-
# printing.py
# Printing module
# Copyright 2006 Giuseppe Venturini

# This file is part of the ahkab simulator.
#
# Ahkab is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# Ahkab is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License v2
# along with ahkab.  If not, see <http://www.gnu.org/licenses/>.

"""
This is the printing module of the simulator.

Using its functions, the output will be somewhat uniform.
"""

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import contextlib
import sys
import os

import tabulate
import numpy as np

from . import options
from . import py3compat

if py3compat.PY2:
    import codecs
    UTF8Writer = codecs.getwriter('utf8')
    sys.stdout = UTF8Writer(sys.stdout)

def open_utf8(filename):
    """Get a file handle wrapped in a UTF-8 writer

    The file is opened in ``w`` mode.

    Unicode allows us to write fancy symbols but its handling across different
    major Python version can be pretty painful. /rant

    **Parameters:**

    filename : string
        The file name, just like you would pass to Python's built-in ``open()``
        method.

    **Returns:**

    fp : codecs.UTF8Writer object
        The wrapped file pointer.
    """
    fp = open(filename, 'w')
    if py3compat.PY2:
        UTF8Writer = codecs.getwriter('utf8')
        fp = UTF8Writer(fp)
    return fp

def print_analysis(an):
    """Prints a analysis to stdout, with the netlist syntax

    **Parameters:**

    an : dict
        an analysis description.

    """
    if an["type"] == "op":
        print(".op", end="")
        for x in an:
            if x == 'type' or x == 'outfile' or x == 'verbose':
                continue
            print(" %s=%s" % (x, an[x]), end="")
        print("")
    elif an["type"] == "dc":
        print(".dc %(source)s start=%(start)g stop=%(stop)g step=%(step)g type=%(sweep_type)s" % an)
    elif an["type"] == "tran":
        sys.stdout.write(".tran tstep=" + str(an["tstep"]) + " tstop=" + str(
            an["tstop"]) + " tstart=" + str(an["tstart"]))
        if an["method"] is not None:
            print(" method=" + an["method"])
        else:
            print("")
    elif an["type"] == "shooting":
        sys.stdout.write(".shooting period=" + str(
            an["period"]) + " method=" + str(an["method"]))
        if an["points"] is not None:
            sys.stdout.write(" points=" + str(an["points"]))
        if an["step"] is not None:
            sys.stdout.write(" step=" + str(an["step"]))
        print(" autonomous=", an["autonomous"])


def print_general_error(description, print_to_stdout=False):
    """Prints a error message to stderr.

    **Parameters:**

    description : str
        the error's description

    print_to_stdout : bool, optional
        force printing to ``stdout`` instead.

    """
    the_error_message = "E: " + description
    if print_to_stdout:
        print(the_error_message)
    else:
        sys.stderr.write(the_error_message + "\n")
    return None


def print_warning(description, print_to_stdout=False):
    """Prints a warning message to stderr.

    **Parameters:**

    description: str
        the warning's description

    print_to_stdout : bool, optional
        force printing to ``stdout`` instead.

    """
    the_warning_message = "W: " + description
    if print_to_stdout:
        print(the_warning_message)
    else:
        sys.stderr.write(the_warning_message + "\n")
    return None


def print_info_line(msg_relevance_tuple, verbose, print_nl=True):
    msg, relevance = msg_relevance_tuple
    if verbose >= relevance:
        with printoptions(precision=options.print_precision,
                          suppress=options.print_suppress):
            if print_nl:
                print(msg)
            else:
                print(msg, end=' ')
                sys.stdout.flush()
    # else: suppressed.


def print_parse_error(nline, line, print_to_stdout=False):
    """Prints a parsing error to stderr.

    **Parameters:**

    nline : int,
        number of the line on which the error was found

    line : str
        the line of the file

    print_to_stdout : bool, optional
        print to stdout instead.
    """
    print_general_error(
        "Parse error on line " + str(nline) + ":", print_to_stdout)
    if print_to_stdout:
        print(line)
    else:
        sys.stderr.write(line + "\n")
    return None


def print_symbolic_results(x):
    keys = list(x.keys())
    keys.sort(lambda x, y: cmp(str(x), str(y)))
    for key in keys:
        print(str(key) + "\t = " + str(x[key]))
    return None


def print_symbolic_transfer_functions(x):
    keys = list(x.keys())
    keys.sort(lambda x, y: cmp(str(x), str(y)))
    for key in keys:
        print(str(key) + " = " + str(x[key]['gain']))
        print('\tDC: ' + str(x[key]['gain0']))
        for index in range(len(x[key]['poles'])):
            print('\tP' + str(index) + ":", str(x[key]['poles'][index]))
        for index in range(len(x[key]['zeros'])):
            print('\tZ' + str(index) + ":", str(x[key]['zeros'][index]))
    return None


def print_symbolic_equations(eq_list):
    print("+--")
    for eq in eq_list:
        print("| " + str(eq))
    print("+--")
    return


def print_result_check(badvars, verbose=2):
    """Prints out the results of the OP check performed by results.op_solution.gmin_check
    It assumes one set of results is calculated with Gmin, the other without.
    badvars: the list returned by results.op_solution.gmin_check

    Returns: None
    """
    if len(badvars):
        print("Warning: solution is heavvily dependent on gmin.")
        print("Affected variables:")
        for bv in badvars:
            print(bv)
    else:
        if verbose:
            print("Difference check is within margins.")
            print("(Voltage: er=" + str(options.ver) + ", ea=" + str(options.vea) + \
                ", Current: er=" + \
                str(options.ier) + ", ea=" + str(options.iea) + ")")
    return None


def table(data, *args, **argsd):
    return tabulate.tabulate(data, *args, **argsd)

def table_print(twodarray, separator='  '):
    print(tabulate.tabulate(twodarray))

@contextlib.contextmanager
def printoptions(*args, **kwargs):
    original = np.get_printoptions()
    np.set_printoptions(*args, **kwargs)
    yield
    np.set_printoptions(**original)

locale = os.getenv('LANG')
if not locale:
    print_warning('Locale appears not set! please export LANG="en_US.UTF-8" or'
                  ' equivalent, ')
    print_warning('or ahkab\'s unicode support is broken.')

