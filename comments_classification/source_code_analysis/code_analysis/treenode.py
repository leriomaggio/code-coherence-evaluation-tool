"""
:Author: Valerio Maggio
:Organization: University of Naples Federico II
:Contact: valerio.maggio@unina.it

"""

from antlr3.tree import CommonTree


class CustomNode(CommonTree):

    DEFAULT_TYPE = 'GENERIC_TYPE'

    def __init__(self, payload):

        super(CustomNode, self).__init__(payload)

        # Features
        self.is_statement = False
        self.is_class_statement = False
        self.is_method_statement = False

        self._head_words = None
        self._head_words_ord = None

        self._context = None

        self._instruction_class = None
        # The "type" of the node, according to Language Specifications
        self._instruction = None

        self._identifier_type = None

    def _forXml(self):
        '''
        Python version of forXml function originally written in Java
        http://www.javapractices.com/topic/TopicAction.do?Id=96
        distributed under the license http://creativecommons.org/licenses/by/3.0/
        '''
        ret = super(CustomNode,self).__str__()
        ret = ret.replace('&','&amp;')
        ret = ret.replace('<','&lt;')
        ret = ret.replace('>','&gt;')
        ret = ret.replace('\"','&quot;')
        ret = ret.replace('\'','&#039;')
        return ret

    def __str__(self):
        return self._forXml()

    @property
    def xml_node_name(self):
        if self.is_class_statement:
            return "class_statement_node"
        if self.is_method_statement:
            return "method_statement_node"
        if self.is_statement:
            return "statement_node"
        return "node"

    def propagateHeadWords(self):
        '''
        Head words propagation algorithm
        '''

        from copy import copy
        from source_code_analysis.code_analysis.JavaParser import tokenNames as token_names

        if self.is_leaf:
            self._head_words = [self.node_name]
            self._head_words_ord = -1
        else:
            for child in self.xchildren:
                child.propagateHeadWords()

            sorted_children = sorted(self.children, cmp=None, key=lambda x: x._head_words_ord)
            least_number = 1
            target = sorted_children[0]._head_words_ord # first element
            for node in sorted_children[1:]:
                if node._head_words_ord == target:
                    least_number += 1

            hws = list()
            if least_number == len(sorted_children):
                # Get headwords from all children
                node_list = copy(self.children)
            else:
                node_list = sorted_children[:least_number]

            node_list_copy = copy(node_list)
            for node in node_list:
                curr_node_hws = node.head_words
                for word in curr_node_hws:
                    if word in token_names and word.isupper():
                        curr_node_hws.remove(word)
                        # UPPERCASED Token names are fake NODE NAMES inserted
                        # in AST during the parsing phase.
                        # If a headword accidentally is named as a Lowercased
                        # token name, it is considered valid
                        # e.g. class Identifier in JabRef Project

                if len(curr_node_hws):
                    hws.extend(curr_node_hws)

            if not len(hws):
                # In the worst case, all head_words of selected ord number are all token Names
                # In this case, the first valid head_words set is considered
                if len(sorted_children) > least_number:
                    hws.extend(sorted_children[least_number].head_words)
                else:
                    # In this case, all the possible headwords where keywords
                    # and the current_node has no other child from who can
                    # get headwords so assign to headwords list the list of
                    # keywords trimmed instead of empty list
                    for node in node_list_copy:
                        hws.extend(node.head_words)

            self._head_words = sorted(set(hws)) # The set is useful to eliminate repetitions
            self._head_words_ord = target + 1


    def propagateContext(self):
        '''
            Context propagation algorithm.
            If a node is a statement_node, the Context of the node is itself
            else the Context of the node is the node_type of the parent that
            will represent the closer statement node in hierarchy in which
            the current tree node is used (in src code)
        '''

        if self.is_class_statement or self.is_method_statement:
            self._context = self.node_type
        elif not self.parent or not self.parent._context:
            self._context = None
        else:
            self._context = self.parent.get_context()

        for child in self.children:
            child.propagateContext()

    def get_context(self):
        if self.is_statement:
            return self._instruction_class
        return self.parent.get_context()

    @property
    def is_leaf(self):
        return len(self.children) == 0

    @property
    def node_name(self):
        return self._forXml()

    @property
    def xchildren(self):
        for child in self.children:
            yield child

    @property
    def head_words(self):
        if not self._head_words:
            self.propagateHeadWords()
        return self._head_words

    @property
    def head_words_ord(self):
        return self._head_words_ord

    @property
    def context(self):
        if not self._context:
            self.propagateContext()
        return self._context

    @property
    def instruction_class(self):
        if not self._instruction_class:
            self._instruction_class = self.node_name
        return self._instruction_class

    @instruction_class.setter
    def instruction_class(self, ntype):
        self._instruction_class = ntype

    @property
    def instruction(self):
        if not self._instruction:
            self._instruction = self.node_name
        return self._instruction

    @instruction.setter
    def instruction(self, type_ls):
        self._instruction = type_ls

    def _get_node_identifier_type(self):
        return self._identifier_type

    def _set_node_identifier_type(self, id_type):
        self._identifier_type = id_type

    identifier_type = property(fget=_get_node_identifier_type, fset=_set_node_identifier_type)
