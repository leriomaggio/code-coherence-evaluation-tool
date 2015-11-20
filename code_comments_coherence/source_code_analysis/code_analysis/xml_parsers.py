# -*- coding: utf-8 -*-
from xml.parsers import expat
from os.path import sep as path_sep

# ------------------------
# Django dependency Import
# ------------------------
from django.conf import settings

SOURCE_ROOT = settings.MEDIA_ROOT

class ParsedTreeNode(object):
    """
    A parsed XML Element Node. 
    This class embeds all the information associated to a XML node 
    and exposes them (via properties and methods) in a more OOP friendly way.
    """

    def __init__(self, name, attributes):
        """
            Saves the Tag name and attributes dictionary
        """

        self.name = name
        self.attributes = attributes

        # Reference ID - self assigned during parsing
        self._id = -1

        #Initialize children list to empty list
        self.children = list()
        self.parent = None  # Reference to the parent node

        self._ref_filename = None
        self._ref_filepath = None
        
        self._repr_name = None  # Representation name for the node (see code_label property)

        self._start_line = None
        self._end_line = None

        self._instruction_class = None
        self._instruction = None

    def add_child(self, element):
        self.children.append(element)

    def get_attribute(self, attr_name):
        """
            Returns the value associated to the input
            *attr_name* if it exists, None instead.
        """
        if attr_name in self.attributes:
            return self.attributes.get(attr_name)
        return None

    def get_elements(self, name=''):
        """
        If *name* is not None or empty string, this functions
        returns all the children whose name matches with the *name*.
        Conversely, the entire list of children is returned.
        """
        if name:
            return filter(lambda node: node.name == name, self.children)
        else:
            return self.children

    @staticmethod
    def from_xml_to_unicode(value):
        """
        Sanitize the input _value_ in a Unicode-compliant format.
        """
        value = str(value).strip()
        value = value.replace('&#039;', '\'')
        value = value.replace('&quot;', '"')
        value = value.replace('&gt;', '>')
        value = value.replace('&lt;', '<')
        value = value.replace('&amp;', '&')
        return value

    @staticmethod
    def from_unicode_to_xml(xml_line):
        """
        Sanitize the input _value_ in a XML-compliant format.
        """
        if xml_line.find("name=") != -1:
            value = xml_line[xml_line.find("name=")+len('name="'):xml_line.find('" line')]
            value = value.replace('&', '&amp;')
            value = value.replace('>', '&gt;')
            value = value.replace('<', '&lt;')
            value = value.replace("'", '&#039;')
            value = value.replace('"', '&quot;')
            new_xml_line = xml_line[:xml_line.find("name=")+len('name="')] + value + \
                           xml_line[xml_line.find('" line'):]
            return new_xml_line
        else:
            return xml_line

    def repr_in_xml(self, indent=''):
        """
            Represent the tree rooted in self as a
            XML tree.
        """
        tagline = '%s<%s name="%s" line="%d" instruction_class="%s" instruction="%s">\n' % (
            indent, self.name, self.label, self.line_number, self.instruction_class,
            self.instruction)

        if self.is_leaf_node:
            tagline += '</%s>' % self.name
            return tagline
        for child in self.children_nodes:
            tagline += child.repr_in_xml(indent=indent + "  ")
        tagline += indent + "</%s>\n" % self.name
        return tagline

    def to_json(self):
        json_repr = {
            'name': self.name,
            'label': self.label,
            'node_type': self.instruction_class,
            'instruction': self.instruction,
            'id': self.node_id,
            'start_line': self.startline,
            'end_line': self.endline,
            'filepath': self.src_filepath,
            'filename': self.src_filename
        }
        children = []
        for c in self.children:
            cn_json = c.to_json()
            children.append(cn_json)
        json_repr['children'] = children
        return json_repr

    @classmethod
    def from_json(cls, json):
        node = cls(json['name'], {
            'name': json['label']
        })
        node.src_filepath = json['filepath']
        node.src_filename = json['filename']
        node.node_id = json['id']
        node.instruction = json['instruction']
        node.node_type = json['node_type']
        node.startline = json['start_line']
        node.endline = json['end_line']
        node.children = [cls.from_json(c) for c in json['children']]
        return node

    def as_ptb(self):
        """
        Represent the tree (rooted in self) in the Penn Tree Bank (PTB) format
        """
        
        # TODO: Change recursive implementation into an iterative one
        
        if self.is_leaf_node:
            label = self.label.replace('(', 'LBR').replace(')', 'RBR')
            return '(%s %s)' % (self.instruction, label)

        ptb = '(%s ' % self.instruction
        for cn in self.children_nodes:
            ptb += cn.as_ptb()
        ptb += ')'
        return ptb

    def __repr__(self):
        if self.src_filename:
            return "[%s] %s - (%d, %d)" % (self.src_filename, self.code_label,
                                       self.startline, self.endline)
        else:
            return "%s - (%d, %d)" % (self.code_label, self.startline, self.endline)

    def __str__(self):
        return str(repr(self))

    def __hash__(self):
        """
        So far, the hash key depends on the machine where 
        the parsing took place as it is based on the `_ref_filepath` attribute.
        In the generale case, this doesn't matter as it is just a way to encode  
        the `ParsedTreeNode` in a Python dictionary
        (see `Xml2ObjectParser.encode_node`).
        """

        # FIXME: There's a known Bug affecting this hashing strategy!
        #        If we encode the same file at two different granularity levels 
        #        (e.g., ClassLevel and Method Level), there will be no correspondence
        #        between the hashing value of the *same* nodes. For example, if we perform a 
        #        MethodLevel parsing, the value of the hashing of upper level *class nodes* 
        #        (i.e., `node.is_class == True`) will be different from those
        #        calculated for the *same* nodes instances performing a ClassLevel parsing.
        #        This is because so far the hashing function depends on attributes whose
        #        value change if we call the hash during and/or after the parsing of the whole
        #        file has been completed
        #        (namely `self.startline` and `self.endline`). In fact, in the former case, 
        #        the values of these attributes will be equal to 0 as no child has been added yet.
        return hash('%s_%d_%d_%d' % (self.code_label, self.startline, self.endline,
                                     len(self.children)))

    # ===== Properties =====

    @property
    def children_nodes(self):
        for cn in self.children:
            yield cn

    @property
    def parent_node(self):
        return self.parent

    @parent_node.setter
    def parent_node(self, pnode):
        self.parent = pnode

    @property
    def is_leaf_node(self):
        return len(self.children) == 0

    @property
    def is_filename(self):
        return self.name.lower() == "srcfile"

    @property
    def is_class(self):
        return self.name.lower() == "class_statement_node"

    @property
    def is_method(self):
        return self.name.lower() == "method_statement_node"

    @property
    def is_generic_method(self):
        return self.name.lower() == "method_statement_node" \
            and not self.instruction == "ANNOTATION_METHOD_DECLARATION"

    @property
    def is_statement(self):
        return self.name.lower() == "statement_node"

    @property
    def is_identifier(self):
        return self.instruction_class == "IDENTIFIER"

    @property
    def instruction_class(self):
        if not self._instruction_class:
            attr_name = self.get_attribute("instruction_class")
            self._instruction_class = attr_name if attr_name else self.attributes.get("node_type")
        return self._instruction_class

    @instruction_class.setter
    def instruction_class(self, instruction_class_value):
        self.instruction_class = instruction_class_value

    @property
    def instruction(self):
        if not self._instruction:
            attr_name = self.get_attribute("instruction")
            self._instruction = attr_name if attr_name else self.get_attribute("node_type_ls")
        return self._instruction

    @instruction.setter
    def instruction(self, instruction_value):
        self._instruction = instruction_value

    @property
    def label(self):
        name = self.attributes.get('name')
        if name.isupper():
            name = name.lower()
        return name

    @property
    def code_label(self):
        """
        The `code_label` property corresponds to a Natural Language representation of
        current node.
        This NL node representation is determined as it follows:
        *   if the node is a leaf node, its code label is its own label attribute.
        *   if the node is an internal node, its code label corresponds to the one associated
            to the first leaf node rightmost among its children whose `instruction` attribute is equal
            to `IDENTIFIER`. In case there isn't any node matching the above criterion,
            the `code_label` attribute will correspond to the ones associated to every
            child node (separated by a dash).
        """
        if not self._repr_name:
            if self.is_leaf_node:
                self._repr_name = self.label
            else:
                for ch_node in reversed(self.children):
                    if ch_node.is_leaf_node and ch_node.instruction == 'IDENTIFIER':
                        self._repr_name = ch_node.label  # Get the label of leaf node
                        break
                if not self._repr_name:
                    # This is the case when current node has not leaf nodes
                    # among its children. In this case, code_label will be equal to the
                    # concatenation of all code_label properties of children
                    self._repr_name = '-'.join([n.code_label for n in self.children_nodes])
        return self._repr_name

    @property
    def line_number(self):
        """
        Get line number attribute and covert it
        to an int value.
        Return 0 (zero) if line_number is None or
        it is not set.
        """
        line_no_attr = self.get_attribute('line')
        line_no = line_no_attr if line_no_attr else self.get_attribute('line_number')
        if not line_no:
            return 0
        return int(line_no)

    # ID property (get and set)
    @property
    def node_id(self):
        return self._id

    @node_id.setter
    def node_id(self, id_value):
        self._id = id_value

    @property
    def src_filename(self):
        if not self._ref_filename and self.parent:
            self._ref_filename = self.parent.src_filename
        return self._ref_filename

    @src_filename.setter
    def src_filename(self, filename):
        self._ref_filename = filename

    @property
    def src_filepath(self):
        if not self._ref_filepath and self.parent:
            self._ref_filepath = self.parent.src_filepath
        return self._ref_filepath

    @src_filepath.setter
    def src_filepath(self, filepath):
        self._ref_filepath = filepath

    @property
    def src_relative_filepath(self):
        """Returns the relative source file path, i.e., the `src_filepath` without SOURCE_ROOT"""
        relative_filepath = self.src_filepath.replace(SOURCE_ROOT, '')
        if relative_filepath.startswith(path_sep):
            return relative_filepath[1:]
        return relative_filepath

    @property
    def startline(self):
        if not self._start_line:
            # if attribute has not ever been set
            self._start_line = self.line_number
            if not self._start_line:

                # if the line number is equal to zero (fake node in tree)
                # get the first startline != 0 looking at children
                for node in self.iter_breadth_first(include_self=False):
                    # iter children breadth-first
                    if node.startline:
                        self._start_line = node.startline  # Catcha!
                        break

        return self._start_line

    @startline.setter
    def startline(self, value):
        self._start_line = value

    def _get_max_recursive_endline(self):
        """
            Get the 'deepest' end_line value
            by traversing depth-first the subtrees
            rooted in children nodes.
        """
        return max([child.endline for child in self.children_nodes])

    @property
    def endline(self):
        if not self._end_line:
            if self.is_leaf_node:
                self._end_line = self.line_number
            else:
                self._end_line = self._get_max_recursive_endline()
        return self._end_line

    @endline.setter
    def endline(self, value):
        self._end_line = value

    # ===== Traversal Algorithms ======
    def iter_depth_first(self, include_self=True):
        # Depth first traversal
        stack = [self, ] if include_self else reversed(self.children)
        while stack:
            current_node = stack.pop(0)
            yield current_node
            stack.extend(reversed(current_node.children))

    __iter__ = iter_depth_first

    def iter_breadth_first(self, include_self=True):
        # Breadth first traversal
        stack = [self, ] if include_self else [child for child in self.children]
        while stack:
            current_node = stack.pop(0)
            yield current_node
            stack.extend(current_node.children)
    #__iter__ = iter_breadth_first


class Xml2ObjectParser(object):
    """
    XML to Object Converter.
    This solution is a modification of the original idea presented
    in the Cookbook recipe "12.5 Converting an XML Document into a Tree of Python Objects".
    
    The basic idea of this recipe is to load an XML object into memory and 
    map the document into a tree of Python objects.
    
    The additional requirement (and so, its modification) regards the fact that
    the parser should be aware that input XML files correspond to ASTs.
    In particular, the parser returns a list of XML subtrees (represented as 
    Python objects - see `ParsedTreeNode` class) depending on the selected 
    parsing granularity.
    
    The different parsing granularity is implemented through subclassing: this class is indeed
    an ABC with a set of *Template Methods* [pattern][0] invoked in the main `parse()` method.
    
    For more details, see classes `ClassExtractor`, `MethodExtractor`, and `StatementExtractor`.
    
    [0]: http://en.wikipedia.org/wiki/Template_method_pattern
    """

    def __init__(self, encode_node=True):
        """
        This class handles the following parsing structure:

        - upper_level_info: Dictionary containing references to the upper_level_nodes
            parsing strcutures (i.e., the list of root_trees and upper_level_stack)

        - upper_level_stack: Parsing stack for upper_level_nodes (as Python list)

        - trees: Dictionary containing references to trees and subtrees related to the current
        parsing level

        - level_keys: List containing the keys of every upper_level_nodes usedin upper_level_info
        dictionary (Useful to correctly reference the upper_level_info - i.e.,
        the parsing context - to switch to.)

        - node_stack: Current (sub)tree parsing stack.
        
        Parameters:
        ===========
        
        - encode_node: Decide if an integer encoding should be used to enconde upper_level nodes
                         that will become keys in the `upper_level_info` map (default: True).
                         If it is `False`, the hashable instance will be used instead.
        """
        self.upper_level_info = dict()

        self.upper_level_stack = None
        
        self.node_encoding = encode_node

        self._level_idx = -1
        self.level_keys = list()

        # Single root_nodes info
        self.trees = None
        self.node_stack = None

        self.current_tree_index = -1

        self._id_counter = 0

        self.ref_src_filename = ''
        self.ref_src_relative_filepath = ''
        self.ref_src_filepath = ''

    # ===== Template Methods =====

    def is_root(self, node):
        """
        [Template method]
        The implementation should return 
        wether or not the input node is a 
        **root node**.
        """
        raise NotImplementedError

    def is_upper_level(self, node):
        """
        [Template method]
        The implementation should return `True` (`False`) 
        depending if the input node is (is not) an 
        **upper_level** node.
        """
        raise NotImplementedError

    def encode_node(self, node, encode=True):
        """
        The method returns a unique
        key for an input *upper_level_node*.
        This is useful to correclty map the 
        root nodes of subtrees extracted from the input
        XML file.
        
        In particular, if the `encode` parameter is set to `False`, 
        the generated hierarchy structure will 
        contain a direct reference to the instance of the 
        upper level node as key.
        However, plese note that so far the parsing algorithm
        does not add any child node to this one.
        This strategy only works because `ParsedTreeNode` instances are hashable objects.
        
        On the other hand, if the `encode` parameter is `True` (default value), 
        the `hash(node)` will be returned as key.

        In this way, no instance will be kept in the map structure, but
        the overall space required will be by far more efficient.
        
        The value of the `encode` parameter corresponds to the `node_encoding`
        attribute of the `Xml2ObjectParser` class, that is set in the constructor.
        
        """
        if encode:
            return hash(node)  # integer key - hashing of input ParsedTreeNode instance.
        return node  # the node instance is hashable, so no encoding is really applied here.
        

    # ===== SAX Parser Hooks =====

    def start_element(self, name, attributes):
        """
        Callback invoked by the SAX parser whenever an *open* XML tag
        has been found.
        
        Since the XML parser should implement a parsing strategy that is
        aware of multiple nesting (sub)trees, i.e., classes nested to classes 
        (internal classes), methods nested to method and so forth, 
        the algorithms distinguish between two different kinds of *root nodes*:
        - upper level nodes
        - root nodes

        The two kinds are different according to the selected parsing granularity
        level (see Template Methods).
        **Upper level nodes** are those that contains all the "main" subtrees, while
        **root nodes** are the roots of subtrees corresponding to the selected granularity.
        
        For example, in case of a "Class-level" granularity, *upper level nodes* are those 
        corresponding to the source files containig them, while *root nodes* correspond to 
        class nodes.
        On the other hand, in case of a "Method-level" granularity, *root nodes* are method
        nodes while *upper level nodes* correspond to class nodes (i.e., classes that contains
        methods)
        
        Note that this parsing strategy will fail in getting methods/functions in languages
        such as Python that do not require a method/function to be defined necessarily inside
        a Class.
        """

        #------
        #  TODO: Write down few lines to describe *how* the method works
        #------
        node = ParsedTreeNode(name, attributes)

        if node.is_filename:
            self.ref_src_filename = attributes.get('name')
            self.ref_src_filepath = attributes.get('file_path')

        if not self.upper_level_info.keys() and not self.is_upper_level(node):
            # So far, no upper level nodes have been found. In this case, simply discard the
            # current node!
            return

        if self.is_upper_level(node):
            # Assign src_filename to root node
            node.src_filename = self.ref_src_filename
            node.src_filepath = self.ref_src_filepath

            self._level_idx += 1
            self.current_tree_index = -1

            node_key = self.encode_node(node, encode=self.node_encoding)
            self.upper_level_info[node_key] = {'trees': [], 'level_stack': [node]}
            self.level_keys.append(node_key)

            # Assign current global_stack and trees list
            self.trees = self.upper_level_info[node_key]['trees']

            # Set upper_level_stack to the reference in upper_level_info dictionary
            self.upper_level_stack = self.upper_level_info[node_key]['level_stack']

        if not self.is_root(node) and not len(self.trees):
            # So far no root nodes (aka subtree) has been found, so discard the current node!
            # TODO: Check if this situation is possible - in general, I think so.
            return

        if self.is_root(node):
            # This is a Root Node, i.e., the root of a new subtree to build up recursively

            # Assign src_filename to root node
            node.src_filename = self.ref_src_filename
            node.src_filepath = self.ref_src_filepath

            # Assign node ID
            self._id_counter = 0
            node.node_id = self._id_counter
            self._id_counter += 1

            # Add to global stack
            self.upper_level_stack.append(node)

            self.trees.append({'root': node, 'stack': [node]})
            self.current_tree_index = len(self.trees) - 1
            self.node_stack = self.trees[self.current_tree_index]['stack']

        elif self.node_stack:  # Check if there's any subtree under construction

            # This is an internal Node!

            # Assign node ID
            node.node_id = self._id_counter
            self._id_counter += 1

            # Get Parent node
            parent = self.node_stack[-1]
            # Add the new child to the parent node
            parent.add_child(node)
            # Add reference to parent node
            node.parent_node = parent

            self.node_stack.append(node)
            self.upper_level_stack.append(node)

    def end_element(self, name):
        """
            Callback invoked by the SAX parser whenever a _closed_ XML tag
            has been found.    
        """
        #------
        #  TODO: Write down few lines describing the logic of the method
        #------

        if not self.upper_level_stack or not len(self.upper_level_stack):
            # No nodes has been found so far and so there's nothing to remove. So keep moving ahead.
            return

        if not self.node_stack or not len(self.node_stack):
            if len(self.upper_level_stack) == 1 and name == self.upper_level_stack[0].name:
                # No subtree has been found but only upper_level_nodes. In this case, move ahead
                # to remove the node!
                pass
            else:
                # Nothing to remove in the current stack
                return

        self.upper_level_stack.pop()  # pop from the global_stack

        if not len(self.upper_level_stack):  # Upper_level_stack is emtpy!

            self.level_keys.pop()
            self._level_idx -= 1  # Update level counter

            if self._level_idx < 0:
                return  # We're done!

            # Restore previous parsing context
            level_ref = self.upper_level_info[self.level_keys[self._level_idx]]

            self.trees = level_ref['trees']
            self.upper_level_stack = level_ref['level_stack']
            self.current_tree_index = len(self.trees) - 1

            if self.current_tree_index >= 0:
                self.node_stack = self.trees[self.current_tree_index]['stack']
            else:
                self.node_stack = None
            return

        # Delete closed XML element - no index so last element as default
        removed_node = self.node_stack.pop()

        # If the consumed node was a root node, update current parsing stack
        # switching to the previous subtree in the list that has been found so far.
        if self.is_root(removed_node):
            # Check if current_tree_index must be updated

            self.current_tree_index -= 1
            prev_node_stack = self.trees[self.current_tree_index]['stack']

            while not len(prev_node_stack) and self.current_tree_index >= 0:
                self.current_tree_index -= 1
                prev_node_stack = self.trees[self.current_tree_index]['stack']

            if self.current_tree_index < 0:
                self.node_stack = None
                self.trees[self.current_tree_index]['stack'] = []
            else:
                self.node_stack = self.trees[self.current_tree_index]['stack']

    def parse(self, filename):
        """
        Parse the XML content of the given file
        """
        return self.parse_content(open(filename).read())
        

    def parse_content(self, xml_content):
        """
        Parse the input XML file of an AST, hooking self methods
        to Expat SAX parser.
        
        Returns the exit code of the parser together with a list of
        all root_nodes (pointing to parsed subtrees) and a map
        containing references to root nodes grouped by upper_level_nodes.
            
        """
        #Create an Expat Parser
        parser = expat.ParserCreate()

        #Set expat event handler to class custom methods
        parser.StartElementHandler = self.start_element
        parser.EndElementHandler = self.end_element

        # Parse the XML file
        parser.Parse(xml_content, 1)

        roots_map = dict()
        for key, info in self.upper_level_info.iteritems():
            roots_map[key] = [tree['root'] for tree in info['trees']]

        flat_roots_list = list()
        for tree_list in roots_map.itervalues():
            for root in tree_list:
                flat_roots_list.append(root)

        return flat_roots_list, roots_map


# Different Granularity Extractors


class ClassLevelParser(Xml2ObjectParser):
    """
    Class level AST parser
    
    Details:
    - Upper level node: filename
    - root node: class node
    """

    def is_root(self, node):
        return node.is_class

    def is_upper_level(self, node):
        return node.is_filename


class MethodLevelParser(Xml2ObjectParser):
    """
    Method level AST parser.
    
    Details:
    - Upper level node: class node
    - root node: method node
    """

    def is_root(self, node):
        return node.is_method

    def is_upper_level(self, node):
        return node.is_class


class StatementLevelParser(Xml2ObjectParser):
    """
    Statement Level AST parser
    
    Details:
    - Upper level node: method node
    - root node: statement node
    """

    def is_root(self, node):
        return node.is_statement

    def is_upper_level(self, node):
        return node.is_method


class XMLMethodTreeParser(object):

    def __init__(self):
        '''
        Setting up some attributes used in Tree Parsing
        '''

        self._id_counter = 0  # Node ID Counter
        self.node_stack = list()  # Node Stack
        self.tree_root_node = None  # Initialize (Parsed)Tree Root Node

    def start_element(self, name, attributes):
        """
        Callback invoked by the SAX parser whenever an *open* XML tag
        has been found.

        Note that this parsing strategy will fail in getting methods/functions in languages
        (such as Python) that allow closures.

        This Parser assumes AST-XML-Trees that refers to single methods/functions.
        """

        node = ParsedTreeNode(name, attributes)

        if node.is_method:
            # This is a Root Node, i.e., the root of a new subtree to build up recursively

            # Assign node ID
            node.node_id = self._id_counter
            self._id_counter += 1

            # Initialize the Node Stack w/ the current node.
            self.node_stack = [node]
            self.tree_root_node = node  # NOTE: No Inner Methods or Functions allowed!!

        elif self.node_stack and len(self.node_stack):  # Check if there's any subtree under construction

            # This is an internal Node!

            # Assign node ID
            node.node_id = self._id_counter
            self._id_counter += 1

            # Get Parent node
            parent = self.node_stack[-1]
            # Add the new child to the parent node
            parent.add_child(node)
            # Add reference to parent node
            node.parent_node = parent

            self.node_stack.append(node)

    def end_element(self, name):
        """
            Callback invoked by the SAX parser whenever a _closed_ XML tag
            has been found.
        """

        if not self.node_stack or not len(self.node_stack):
            # Nothing to remove in the current stack
            return
        # Delete closed XML element
        self.node_stack.pop()

    def parse(self, xml_content):
        """
        Parse the input XML file of an AST, hooking self methods
        to Expat SAX parser.

        Returns the exit code of the parser together with a list of
        all root_nodes (pointing to parsed subtrees) and a map
        containing references to root nodes grouped by upper_level_nodes.

        """
        # Create an Expat Parser
        parser = expat.ParserCreate()

        #Set expat event handler to class custom methods
        parser.StartElementHandler = self.start_element
        parser.EndElementHandler = self.end_element

        # Parse the XML file
        parser.Parse(xml_content, 1)
        return self.tree_root_node

