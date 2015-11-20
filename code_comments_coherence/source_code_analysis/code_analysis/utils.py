"""
:Author: Valerio Maggio
:Organization: University of Naples Federico II
:Contact: valerio.maggio@unina.it

"""

import os
from xml_parsers import MethodLevelParser
import sys

#===================
# Utility Functions
#===================

def get_sources_from_dir(root_path, extension):
    """
    This function recursively traverse the input `root_path` and
    returns a list containing the absolute paths of all the files whose
    extension is equal to `extension`
    """
    if not os.path.isdir(root_path):
        raise ValueError('The input root_path is not a valid directory')

    files_list = list()
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            if not filename.startswith('.'):
                filepath = os.path.abspath(os.path.join(root, filename))
                path, ext = os.path.splitext(filepath)
                if ext == extension:
                    files_list.append(filepath)
    return files_list


def parse_xml_files_list(cls_parser, xml_files_list):
    tree_list = list()
    tree_map = dict()
    for xml_filepath in xml_files_list:
        parser = cls_parser()
        tlist, tmap = parser.parse(xml_filepath)
        if tlist:
            tree_list.extend(tlist)
            tree_map.update(tmap)
    return tree_list, tree_map


def extract_trees(xml_folder_name, cls_parser=MethodLevelParser):
    """
    This function parses each xml files found in the
    input _xml_folder_name_ (xml files are identified by
    the .xml file extension) and returns the list of all
    methods found after parsing those files.

    Input xml files should represent code syntax trees.
    """

    xml_files_list = get_sources_from_dir(xml_folder_name, extension='.xml')
    return parse_xml_files_list(cls_parser, xml_files_list)

def set_xml_filepath(xml_dest_folderpath, source_filepath, root_path):
    """
    Returns the filepath of the xml file representing the AST.

    This generated filepath will be composed by a folder path that will reproduce
    the package directory structures of the original source file in
    the input `xml_dest_folderpath`, while the name of the file will be
    the same of the original source file (except for the file extension).
    """
    source_filename = os.path.basename(source_filepath)
    source_file_extension = source_filename.split(os.path.extsep)[1]

    package_folder_path = source_filepath.replace(source_filename, '').replace(root_path, '')
    if package_folder_path.startswith(os.path.sep):
        if len(package_folder_path) > 1:
            package_folder_path = package_folder_path[1:]
        else:
            package_folder_path = ''

    xml_package_folder_path = os.path.join(xml_dest_folderpath, package_folder_path)

    if not os.path.exists(xml_package_folder_path):
        os.makedirs(xml_package_folder_path)

    xml_filename = source_filename.replace(source_file_extension,'xml')

    return os.path.join(xml_package_folder_path, xml_filename)


def print_tree_to_xml(node, indent, outfile=sys.stdout):
    """
    Recursively writes to the input `outfile` the `node`
    in XML format
    """
    node_representation = u'{0}<{1} name="{2}" line="{3}" instruction_class="{4}" ' \
                          u'instruction="{5}">\n'.format(indent, node.xml_node_name,
                                                         node.node_name, node.token.line,
                                                         node.instruction_class, node.instruction)
    outfile.write(node_representation.encode('utf8'))
    for child in node.children:
        print_tree_to_xml(child, indent + "  ", outfile)
    outfile.write(u'{0}</{1}>\n'.format(indent, node.xml_node_name).encode('utf8'))


def ensure_xml_files_folder(src_folder_path):
    # Preprocessing: Check and create the XML destination folder if it does not exist yet!
    xml_folder_path = os.path.join(os.path.dirname(src_folder_path), 'xml_source_files')
    folder_existing = True
    if not os.path.exists(xml_folder_path):
        os.makedirs(xml_folder_path)
        folder_existing = False
    return xml_folder_path, folder_existing