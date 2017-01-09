from __future__ import unicode_literals, print_function
import re

from pypeg2 import *

super_word = re.compile('([\w0-9 +\?!&]+)')


MultiLineComment = comment_c


class EndLineComment(str):
    grammar = "//", re.compile('.*')


class Comment(str):
    grammar = [EndLineComment, comment_c]


class Instruction(str):
    grammar = super_word, ";"


class ConditionType(Keyword):
    grammar = Enum(K("if"), K("while"))


class Condition(List):
    pass


block = "{", maybe_some([Instruction, Comment, Condition]), "}", maybe_some(';')
Condition.grammar = attr("name", ConditionType), '(', attr("condition", super_word), ")",\
            [block, Instruction], maybe_some(Comment)


class Code(List):
    grammar = [Instruction, Condition, MultiLineComment]
