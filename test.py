#!/usr/bin/env python
# Copyright (c) 2012 Matt Giuca <matt.giuca@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Test cases for fusepy.

These run the fuse examples in a separate process, so that we can send SIGINT
to terminate them at the end of each test.
"""

import os
import signal
import subprocess
import tempfile
import time
import unittest

# Name of the python interpreter executable.
PYTHON = 'python'

class FuseTest(unittest.TestCase):
    """Base case for testing a particular fuse program.

    Each subclass tests a different program. The subclass should have an
    attribute called PROGRAM which is a list of strings containing the path to
    the program to test and any arguments to pass to that program, except for
    the path to the mountpoint. This will automatically append the point path
    to the end of the arguments list.

    All test cases will be executed with a running instance of Python
    interpreting the program (which should be hosting a fusepy file system).
    The test cases are executed with the current directory as the mountpoint
    of the file system.
    """

    def setUp(self):
        self.mountpoint = tempfile.mkdtemp()
        args = [PYTHON] + self.PROGRAM + [self.mountpoint]
        self.process = subprocess.Popen(args)
        # Wait for the file system to start up.
        time.sleep(0.10)
        self._oldcwd = os.getcwd()
        os.chdir(self.mountpoint)

    def tearDown(self):
        self.process.send_signal(signal.SIGINT)
        # Wait for the process to shut down.
        for i in range(5):
            if self.process.poll() is not None:
                break
            time.sleep(0.1)
        self.assertTrue(self.process.poll() is not None)
        os.chdir(self._oldcwd)
        os.rmdir(self.mountpoint)

class TestMemory(FuseTest):
    """Test the 'memory' example.

    This serves as the main test suite, since this example provides the
    simplest working fuse filesystem.
    """

    PROGRAM = ['examples/memory.py']

    def testCreate(self):
        """Test create, write, readdir."""
        f = open('test.txt', 'w')
        try:
            f.write('This is a test')
        finally:
            f.close()
        self.assertEqual(os.listdir('.'), ['test.txt'])

    def testRead(self):
        """Test read."""
        f = open('test.txt', 'w')
        try:
            f.write('This is a test')
        finally:
            f.close()
        f = open('test.txt', 'r')
        try:
            self.assertEqual(f.read(), 'This is a test')
        finally:
            f.close()

    def testReadOffset(self):
        """Test read at different offsets."""
        f = open('test.txt', 'w')
        try:
            f.write('\0' * 8000)
            f.write('hello')
            f.write('\0' * 3995)
            f.write('world')
        finally:
            f.close()
        f = open('test.txt', 'r')
        try:
            f.seek(12000)
            self.assertEqual(f.read(), 'world')
            f.seek(8000)
            self.assertEqual(f.read(5), 'hello')
        finally:
            f.close()

if __name__ == '__main__':
    unittest.main()
