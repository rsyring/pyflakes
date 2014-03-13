from pyflakes import messages as m
from pyflakes.api import _re_noqa, _noqa_lines, check
from pyflakes.test.harness import TestCase, ListWriter
from pyflakes.reporter import Reporter


class TestNoQA(TestCase):

    def test_regex(self):
        # simple format
        assert _re_noqa.search('#noqa')
        assert _re_noqa.search('# noqa')
        # simple format is strict, must be at start of comment
        assert not _re_noqa.search('# foo noqa')

        # verbose format (not strict like simple format)
        assert _re_noqa.search('#pyflakes:noqa')
        assert _re_noqa.search('# pyflakes: noqa')
        assert _re_noqa.search('# foo pyflakes: noqa')

        # backwards compatible with flake8
        assert _re_noqa.search('# flake8: noqa')

    def test_checker_ignore_lines(self):
        # ignore same line
        self.flakes('from fu import *', ignore_lines=[1])
        # don't ignore different line
        self.flakes('from fu import *', m.ImportStarUsed, ignore_lines=[2])

    def test_noqa_lines(self):
        self.assertEqual(_noqa_lines('from fu import bar; bar'), [])
        self.assertEqual(_noqa_lines('from fu import * # noqa; bar'), [1])
        self.assertEqual(_noqa_lines('from fu import * #noqa\nbar\nfoo # pyflakes: noqa'), [1, 3])

    def test_check_integration(self):
        """ make sure all the above logic comes together correctly in the check() function """
        reporter = Reporter(ListWriter(), ListWriter())

        result = check('from fu import *', 'test', reporter)

        # errors reported
        self.assertEqual(result, 1)
        self.assertEqual(reporter._stdout.pop(0), "test:1: 'from fu import *' used;"
                         " unable to detect undefined names")

        # same test, but with ignore set
        reporter = Reporter(ListWriter(), ListWriter())

        result = check('from fu import * # noqa', 'test', reporter)

        # errors reported
        self.assertEqual(result, 0)
        self.assertEqual(len(reporter._stdout), 0)
