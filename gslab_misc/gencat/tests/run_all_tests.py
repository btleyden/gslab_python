#! /usr/bin/env python

import unittest

loader = unittest.TestLoader()
tests  = loader.discover('.')

with open('./log/make.log', 'w') as log:
    testRunner = unittest.TextTestRunner(stream = log, verbosity = 2)
    testRunner.run(tests)

with open('./log/make.log', 'r') as log:
    print('\n=== Test results ' + '='*53)
    print(log.read())

