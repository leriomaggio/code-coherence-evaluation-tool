"""
:Author: Valerio Maggio
:Organization: University of Naples Federico II
:Contact: valerio.maggio@unina.it

"""

import os

from utils import set_xml_filepath, print_tree_to_xml, parse_xml_files_list
from xml_parsers import ClassLevelParser


#==============
# Code Analyzer
#==============
class CodeAnalyzer(object):
    """
    Abstract Base Class (ABC) providing the
    parsing interface for code analyzers
    """

    def __init__(self, source_code_files, src_folder_path, xml_folderpath):
        self._files_list = source_code_files
        self._src_folder_path = src_folder_path
        self._xml_destination_folder = xml_folderpath

        self._code_comments_map = list()
        self._xml_files_list = list()

    @property
    def method_comments_map(self):
        return self._code_comments_map

    def parse_source_file(self, filepath):
        """[Template Method] Source file parsing"""
        raise NotImplementedError('Not Implemented')

    def parse_code_comment(self, filepath):
        """[Template Method] Code comments parsing
        """
        raise NotImplementedError('Not Implemented')

    def ast_to_xml(self, filepath, output_xml_filepath, ast):
        src_filename = os.path.basename(filepath)
        with open(output_xml_filepath, 'w') as xml_file:
            xml_file.write("<?xml version=\"1.0\" ?>\n")
            xml_file.write(
                '<srcfile name="%s" file_path="%s" >\n' % (src_filename, filepath))
            print_tree_to_xml(ast, ' ', xml_file)
            xml_file.write('</srcfile>')

    def parse_code_files(self, store_xml_files_list=True):
        """ Parses all the Source files appearing in the `_file_list` attribute.
        If the `store_xml_files_list` is passed to True (default value), the
        `_xml_files_list` attribute is populated while generating corresponding XML files.

        Note: if all the XML files corresponding to the parsed ASTs already exists,
              this method simply returns the list of XML files to parse.
        """
        if store_xml_files_list:
            self._xml_files_list = list()

        for filepath in self._files_list:
            output_xml_filepath = set_xml_filepath(self._xml_destination_folder, filepath,
                                                   self._src_folder_path)

            if not os.path.exists(output_xml_filepath):
                # Parse and generate XML file only once
                try:
                    result = self.parse_source_file(filepath)
                except Exception:
                    pass
                else:
                    self.ast_to_xml(filepath, output_xml_filepath, result.tree)

                    if store_xml_files_list:
                        # Finally add the filepath to the list if and only if no error occurred
                        # during the parsing process.
                        self._xml_files_list.append(output_xml_filepath)
            else:
                if store_xml_files_list:
                    # The file already exists, thus add it to the list and return
                    self._xml_files_list.append(output_xml_filepath)

    def parse_code_classes(self):
        """
        Parse all the Source Code Classes gathered from the list of stored AST XML
        representation.

        Returns:
        --------
        classes: list
            The list of all `ParsedTreeNode` objects referring to Class Nodes
        classes_per_file: dict
            A map containing the list of class nodes along with the corresponding
            source code file path (as key)
        """
        # Step1 : Gather XML files list
        if not self._xml_files_list:
            self.parse_code_files(store_xml_files_list=True)

        # Step 2: Parse all corresponding XML files.
        classes, classes_per_file = parse_xml_files_list(ClassLevelParser, self._xml_files_list)
        return classes, classes_per_file

    def map_code_and_comments(self):
        """ This method is responsible to automatically map
         each comment to each class and its corresponding set of methods.

         Source code comments are stored in a dictionary `self.src_file_comments`,
         whose keys are the corresponding source file path.

        This method only perfomrs the proper association with comments stream and its
        corresponding code class, based on their reference filenames.
        The real core of the code-comments association is delegated to the `CodeCommentMap`
        class.

        (Please, see `CodeCommentMap.map` method for additional informations).
         """

        # Step 1 & 2 : Gather XML files list & Parse all XML-AST files
        classes, classes_per_file = self.parse_code_classes()

        # Step 3: Parse Code Comments
        src_file_comments = dict()
        for filepath in self._files_list:
            key = os.path.basename(filepath)
            src_file_comments[key] = self.parse_code_comment(filepath)

        # Step 4: Perform Code-Comment Association
        for class_list in classes_per_file.itervalues():
            if not class_list:
                continue

            src_filename = class_list[0].src_filename
            if not src_filename in src_file_comments:
                continue
            comment_stream = src_file_comments[src_filename]

            if comment_stream:
                for class_node in class_list:
                    code_comment_map = CodeCommentMap(class_node, comment_stream)
                    code_comment_map.map()
                    self._code_comments_map.append(code_comment_map)




#===================
# Java Code Analysis
#===================
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from Comments import Comments
from treenode import CustomNode

from antlr3 import tree, streams, CommonTokenStream
from antlr3 import HIDDEN_CHANNEL


class CustomNodeAdaptor(tree.CommonTreeAdaptor):

    def createWithPayload(self, payload):
        return CustomNode(payload)


class JavaAnalyzer(CodeAnalyzer):

    def __init__(self, source_files, src_folder_path, xml_dest_folderpath):
        super(JavaAnalyzer, self).__init__(source_files, src_folder_path, xml_dest_folderpath)

    def parse_source_file(self, filepath):
        """
        Parse Java Files.

        Parameter:
        ----------

        filepath : The path to the Java file to be analysed

        Returns:
        --------
        The parsing result.

        Note: An exception is raised if an error occurs during the parsing process
        """
        code_stream = streams.ANTLRFileStream(filepath, encoding='utf-8')
        lexer = JavaLexer(code_stream)
        token_stream = CommonTokenStream(lexer)
        parser = JavaParser(token_stream)

        # Set custom NodeAdaptor
        custom_adaptor = CustomNodeAdaptor()
        parser.adaptor = custom_adaptor  # monkey patching?

        result = parser.compilationUnit()
        return result

    def parse_code_comment(self, filepath):
        comment_stream = streams.ANTLRFileStream(filepath, encoding='utf-8')
        comments_lexer = Comments(comment_stream)
        tokens = CommonTokenStream(comments_lexer)
        return filter(lambda t: t.channel != HIDDEN_CHANNEL, tokens.getTokens())


# Note: The keys of this map should be kept aligned
#       with values reported in `source_code_analysis.settings`
analyzers_map = {
    '.java': JavaAnalyzer,
}


#=============================
# Code-Comment Association Map
#=============================

class CodeCommentMap(object):

    def __init__(self, parsed_class_node, comment_stream):
        # Input data
        self._class_node = parsed_class_node
        self._comment_stream = comment_stream

        self._class_comment = None  # comment associated to the class (node)

        self._comment_statement_map = dict()  # map result

    @property
    def class_node(self):
        return self._class_node

    @property
    def class_comment(self):
        return self._class_comment

    @property
    def methods_comments_map(self):
        """Returns the map containing Method-Comment(s) associations,filtering out
        keys that do not corresponds to methods"""
        methods_comments_map = dict()
        for statement in self._comment_statement_map:
            if statement.is_generic_method:
                methods_comments_map[statement] = self._comment_statement_map[statement]
        return methods_comments_map

    def get_next_eligible_statement(self, iter_statements, target_comment, target_statement):
        """
        Closure used in the main iteration algorithm. This function iterates over
        statements once a new `target_statement` whose `startline` is greater than
        `target_comment.line` has been found.
        """
        last_statement_found = target_statement
        try:
            target_statement = next(iter_statements)
            while (target_comment.line > target_statement.startline):
                last_statement_found = target_statement
                target_statement = next(iter_statements)
            return target_statement, last_statement_found
        except StopIteration:
            return None, last_statement_found

    def _extract_statements_from_class_node(self):
        """
         Mapping Step 0:
        ---------------

        This is not actually a step of the mapping process. That's why I marked this function
        as the Step 0. This is becuase the function is responsible to extract all the statement
        nodes (i.e., attributes and methods) enclosed in the body of the class
        (i.e., CLASS_BODY node).
        """
        class_body = None
        for ch in self._class_node.children_nodes:
            if ch.instruction.lower() in ('class_body', 'interface_body') :
                class_body = ch
                break
        if class_body:  # Class_body node found
            # list of statements in CLASS_BODY (i.e., attributes and methods)
            statement_nodes = list()
            for ch in class_body.children_nodes:
                if ch.is_statement or ch.is_generic_method:
                    statement_nodes.append(ch)
            statement_nodes = sorted(statement_nodes, key=lambda m: m.startline)
        else:
            print 'No CLASS BODY found in current class: {path} '.format(
                path=self._class_node.src_relative_filepath)
            return None

        return statement_nodes

    def _associate_comment_to_class(self, sorted_comments):
        """
         Mapping Step 1:
        ---------------

        This is the first and the simplest step in code-comments association:
        comments in the stream will be iterated once a comment for the
        current class node has been found.

        Parameters:
        -----------
        sorted_comments: the list of comments, sorted by line number.

        """
        iter_comments = iter(sorted_comments)
        current_comment = iter_comments.next()
        for comment in iter_comments:
            if comment.line > self._class_node.startline:
                self._class_comment = current_comment
                break
            current_comment = comment

    def _associate_comments_to_methods(self, pending_comments, sorted_comments, statement_nodes):
        """
         Mapping Step 2:
        ---------------

        This function represents the main core of the Code-Comments Mapping Algorithm.
        In particular this method is responsible to associate each comment to corresponding
        method (discarding possible single/multi line comments appearing in the body
        of methods). Moreover, non-mappable comments will be added to the list of
        `pending_comments` for further processing (see Step 3)

        Parameters:
        -----------
        pending_comments: The list of pending comments (usually empty in input) where pending
                          comments (i.e., comments that could not be mapped to any statement)
                          will be stored.
        sorted_comments: The list of comments, sorted by line number
        statement_nodes: The list of statement nodes appearing in the `CLASS_BODY` node of
                         target class (i.e., `self._class_node`).
                         (See Step 0 for additional info about this).
        """

        # Get only comments whose line are contained in the range of the
        # BODY of Class Node
        # Note: Please note that `self._comment_stream` contains all the comments
        #       appearing in the source file where the class is defined.
        class_boundaries = (self._class_node.startline, self._class_node.endline)
        # Class Body Comments (already sorted)
        class_body_comments = [comment for comment in sorted_comments
                               if (class_boundaries[0] < comment.line < class_boundaries[1])]

        if not class_body_comments:
            print 'No comment found for Class {classname} in File {filename}'.format(
                classname=self._class_node.code_label,
                filename=self._class_node.src_relative_filepath)
            return None

        iter_comments = iter(class_body_comments)
        iter_statements = iter(statement_nodes)
        # Initialise `target_comment` and `target_statement` references.
        target_comment = iter_comments.next()
        target_statement = iter_statements.next()
        last_statement_found = None
        # from collections import defaultdict
        # self._comment_statement_map = defaultdict(list)
        for comment in iter_comments:
            # first of all check current comment
            if target_comment.line > target_statement.startline:
                # We have to iterate statements once an eligible target statements
                # has been found (i.e., a statement whose starting line is less than
                # `target_comment.line`).
                target_statement, last_statement_found = self.get_next_eligible_statement(
                    iter_statements, target_comment, target_statement)

                if not target_statement:  # This happens only if a StopIteration has been raised
                    break  # No more statements to look at

            # this is the case of a possible "good candidate". However there are
            # several verification to be performed before.
            # First of all check that if `target_comment` line is greater than the `endline`
            # of the `last_statement_found` (if any).
            # If not, `target_comment` is contained in the body of a method and
            # *must* be discarded
            if last_statement_found:
                if target_comment.line <= last_statement_found.endline:
                    # if so, the target is a comment in the body of a method (statement)
                    target_comment = comment
                    continue  # Skip this iteration step and go the next one

            # Now Check (current) comment line wrt target statement startline
            if comment.line > target_statement.startline:
                # If so, `target_comment` may be associated to `target_statement`
                self._comment_statement_map.setdefault(target_statement, list())
                self._comment_statement_map[target_statement].append(target_comment)

                # Set `last_statement_found`
                last_statement_found = target_statement
                # Now re-set targets
                target_comment = comment
                try:
                    target_statement = next(iter_statements)  # go ahead with statements
                except StopIteration:
                    break  # In this case, break the loop as not further processing are required.
            else:
                # Current comment is pending
                pending_comments.append(target_comment)
                target_comment = comment  # Change target_comment to the current "next"
        else:
            # Check the association to the last comment
            if target_comment.line > target_statement.startline:
                # This means that the iteration has been exited as all the comments have
                # been iterated. However this does not necessarily means that all the statements
                # have been consumed as well. In fact, we are here (condition True) exactly
                # because there are further methods to iterate and check for association
                target_statement, nope = self.get_next_eligible_statement(iter_statements,
                                                                          target_comment,
                                                                          target_statement)

            # Check that last_statement has been associated to some comment
            # This means that we have terminated the previous loop because we consumed both the
            # list iterators. Note that we already checked (previous `if`) that
            # `target_comment` and `target_statement` are both eligible to be associated
            if target_statement and target_statement in self._comment_statement_map:
                self._comment_statement_map.setdefault(target_statement, list())
                self._comment_statement_map[target_statement].append(target_comment)

    def _manage_pending_comments(self, pending_comments):
        """
        Mapping Step 3:
        ---------------
        Once we have completed "ordinary" associations, we have to look at `pending_comments`.

        Pending comments may be of two types:
        * comments not associated to any method as they're enclosed in the body of method
        * documentation comments that precedes some other javadoc comment.

        Only comments of the latter group will be associated to some method/statement in
        this function.
        Other ones, will be simply discarded.

        Parameters:
        -----------
        pending_comments: The list of pending comments to be processed. This list has been
                          fed during the Statements-Comments Mapping Process (see Step 2)
        """

        if len(self._comment_statement_map.keys()) and len(pending_comments):
            #  First of all, create a temporary structure (dict) whose keys are statement
            # starting lines and values are associated statements
            lookup_map = dict()
            for statement in self._comment_statement_map:
                lookup_map[statement.startline] = statement

            lookup_map_keys = iter(sorted(lookup_map.keys()))
            target_line = lookup_map_keys.next()

            # This should be efficient since pending comments should be sorted by `line`
            # by construction
            for pending_comment in pending_comments:
                for line in lookup_map_keys:
                    if line < pending_comment.line:
                        target_line = line
                        continue

                    # If here, we have that target_line now corresponds to the start_line of a
                    # possible method that enclose comment (in its body)
                    possible_enclosing_statement = lookup_map[target_line]
                    if pending_comment.line > possible_enclosing_statement.endline:
                        # If so, this is NOT a comment in the body of a method
                        statement_to_associate = lookup_map[line]
                        self._comment_statement_map[statement_to_associate].append(pending_comment)
                        break

    def map(self):
        """Map code fragments with corresponding comments based on the line number of
        both, analyzing the file in ascending order (w.r.t. the line number).

        This is the core algorithm of code-comments association. It works as it follows:

         *  Sort Comments and Methods according to their starting line values;
         *  Iterate over the list of classes extracted from the current file.
            * Once you've found a code comment whose start_line is greater than class_startline,
                the preceding comment is associated to the class, if any.
            * Then, for each remaining comments, the algorithm associate them to methods in the same
             way (i.e., once a comment whose start_line is greater than current target method,
             preceding comment is associated to the method as well).

        Return:
        --------
        A map associating a method with the (possible - heuristically assigned)
        corresponding comment. Please note that methods with no corresponding comments
        will be ignored and will not be returned.

        """

        if not self._comment_stream:
            return  # Nothing to map here!

        # first of all, get CLASS_BODY node
        statement_nodes = self._extract_statements_from_class_node()

        if not statement_nodes:
            return  # No statement have been found for target class

        # Sort comments by the line number
        sorted_comments = sorted(self._comment_stream, key=lambda c: c.line)

        # This buffer list is used to store possible pending comments that may occur during
        # the mapping algorithm. This buffer will be consumed after association
        # comment-method has been found.
        #
        # Each possible pending comments in this list will be associated to a method only if
        # its starting line is not enclosed in the body of a method
        # (i.e., this comment is a possible "additional" method comment)
        # Conversely, comments in this list embodied in methods will be discarded.
        #
        # This buffer will be fed every time the current comment
        # has a `next` comment in the comments_list whose line is not greater than the
        # current analysed (CLASS BODY) statement node.
        pending_comments = list()

        # ----------------------------------
        # Step 1: Associate Comment to Class
        # ----------------------------------
        self._associate_comment_to_class(sorted_comments)

        # ---------------------------------------------------------------
        # Step 2: Associate Comments to each statement in the class body
        # ---------------------------------------------------------------
        self._associate_comments_to_methods(pending_comments, sorted_comments, statement_nodes)

        # -------------------------------
        # Step 3: Manage Pending Comments
        # -------------------------------
        self._manage_pending_comments(pending_comments)

        # That's all Folks!
