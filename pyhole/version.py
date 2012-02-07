#   Copyright 2011 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Version Handling"""

from __future__ import with_statement

import os
import sys


__VERSION__ = "0.6.2"


def current_git_hash():
    """Return the current git hash"""
    git_file = ".git/refs/heads/master"
    git_path = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
            os.pardir, os.pardir, git_file))

    if not os.path.exists(git_path):
        git_path = os.getcwd() + "/" + git_file
        if not os.path.exists(git_path):
            git_path = os.getcwd() + "/../" + git_file
            if not os.path.exists(git_path):
                return None

    with open(git_path, "r") as git:
        git_hash = git.read()

    return git_hash[0:5]


def version_string():
    """Return the full version"""
    git_hash = current_git_hash()
    if git_hash:
        return "pyhole v%s (%s) - http://pyhole.org" % (__VERSION__, git_hash)

    return "pyhole v%s - http://pyhole.org" % __VERSION__


def version_hash():
    """Return the current version with git hash"""
    git_hash = current_git_hash()
    return "%s-%s" % (__VERSION__, git_hash)


def version():
    """Return the current version"""
    return __VERSION__
