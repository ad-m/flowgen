#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import unittest
from flowgen import language
from pypeg2 import parse


class TestLanguage(unittest.TestCase):

    def _test_instructions(self, case, result):
        tree = parse(case, language.Instruction)
        self.assertEqual(tree, result)

    def test_instructions_parse(self):
        self._test_instructions('Welcome to code2flow;', 'Welcome to code2flow')
        self._test_instructions('Some text!;', 'Some text!')

    def _test_condition(self, case, condition, code):
        tree = parse(case, language.Condition)
        self.assertEqual(tree.condition, condition)
        self.assertEqual(tree[0], code)

    def test_basic_while(self):
        tree = parse("""while (my_condition) {
                        instruction;
                     }""", language.Condition)
        self.assertEqual(tree.name, 'while')
        self.assertEqual(tree.condition, "my_condition")
        self.assertEqual(tree[0], "instruction")

    def test_basic_if(self):
        tree = parse("""if (example && aa) {
                        instruction;
                     }""", language.Condition)
        self.assertEqual(tree.name, 'if')
        self.assertEqual(tree.condition, "example && aa")
        self.assertEqual(tree[0], "instruction")

    def test_single_line_condition(self):
        tree = parse("if (cond) instruction;", language.Condition)
        self.assertEqual(tree.name, 'if')
        self.assertEqual(tree.condition, "cond")
        self.assertEqual(tree[0], 'instruction')

    def test_condition_with_multiline_comment(self):
        tree = parse("""if (my_condition) {
                                    code;
                        /* XXX */
                     }""", language.Condition)
        self.assertEqual(tree.name, 'if')
        self.assertEqual(tree.condition, "my_condition")
        self.assertEqual(tree[0], "code")
        self.assertEqual(tree[1], "/* XXX */")

    def test_condition_with_end_line_comment(self):
        tree = parse("""if (my_condition) {
                                    code;
                     }; // simple comment""", language.Condition)
        self.assertEqual(tree[0], 'code')
        self.assertEqual(tree[1], 'simple comment')

    def test_condition_with_multiple_comments(self):
        tree = parse("""if (my_condition) {
                                    code;
                     }; // simple comment
                      // second comment
                     """, language.Condition)
        self.assertEqual(tree[1], 'simple comment')
        self.assertEqual(tree[2], 'second comment')

    def test_nested_condition(self):
        tree = parse("""if(my_condition) {
                        if(nested) {
                            code;
                        }
                    }
                    """, language.Condition)
        self.assertEqual(tree.condition, "my_condition")
        self.assertEqual(tree[0].condition, "nested")
        self.assertEqual(tree[0][0], "code")


class ExampleTestLanguage(TestLanguage):
    heading = """Welcome to code2flow;
    """
    condition = """if(In doubt?) {
      Press Help;
      while(!Ready?)
        Read help;
    }
    """
    comment = """// the preview updates
                // as you write"""
    footer = "Improve your workflow!;"""

    def test_heading(self):
        parse(self.heading, language.Instruction)
        parse(self.heading, language.Code)

    def test_condition(self):
        parse(self.condition, language.Condition)
        parse(self.condition, language.Code)

    # def test_comment(self):
    #     parse(self.comment, language.Comment)
    #     parse(self.comment, language.Code)

    def test_footer(self):
        parse(self.footer, language.Instruction)
        parse(self.footer, language.Code)

    # def test_concat(self):
    #     parse(self.heading + self.condition + self.comment + self.footer, language.Code)
