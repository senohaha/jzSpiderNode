#!/usr/bin/env python

from twisted.scripts.twistd import run
from os.path import join, dirname
from sys import argv
import scrapyd


def main():
    print argv
    argv[1:1] = ['-n', '-y', join(dirname(scrapyd.__file__), 'txapp.py')]
    print argv,'kkkk'
    run()

if __name__ == '__main__':
    main()
