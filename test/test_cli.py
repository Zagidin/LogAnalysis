"""
    Проверка на обработку аргументов --report
"""

from unittest.mock import patch
from main import main
import unittest


class TestCLI(unittest.TestCase):

    @patch('sys.argv', ['script.py', 'test1.log', 'test2.log', '--report', 'handlers'])
    def test_valid_args(self):
        args = main({'handlers': 'test'})
        self.assertEqual(args.file, ['test1.log', 'test2.log'])
        self.assertEqual(args.report, 'handlers')

    @patch('sys.argv', ['script.py', 'test1.log', 'test2.log', '--report', 'invalid'])
    def test_invalid_report(self):
        with self.assertRaises(SystemExit):
            main({'handlers': 'test'})