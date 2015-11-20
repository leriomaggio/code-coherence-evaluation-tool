"""
:Author: Valerio Maggio
:Contact: valeriomaggio@gmail.com

"""
from __future__ import division, print_function

"""

    This script extract all the methods from the two versions of the JFreeChart system
    (i.e., so far, the only system with two different versions in the DB) in order to
    collect all the methods that are present in both the two versions.

    To identify if two methods are **exactly** the same, the script considers
    the tuple:

        (Class Name, Method Name, Type Parameters)

    Once all these methods have been collected, an Excel (.xlsx) report file
    is written in order to proceed to the comparison of comments and source code
    that may have changed between the two versions.

    The Excel file will contain the following information:

        Method1 Method2 CoherenceMethod1 CoherenceMethod2 ComparisonInfo Notes
"""

from django.conf import settings
from code_comments_coherence import settings as comments_classification_settings
settings.configure(**comments_classification_settings.__dict__)

# Import Model Classes
from source_code_analysis.models import SoftwareProject

from lxml import etree  # imported to parse method XML parse trees

import xlsxwriter  # To generate final report file

# Import Kernel Function to Detect Clones
from source_code_analysis.code_analysis.kernels import contiguous_tree_kernel
from source_code_analysis.code_analysis.xml_parsers import XMLMethodTreeParser, ParsedTreeNode
from xml.parsers.expat import ExpatError
from nltk.tokenize import wordpunct_tokenize
# from itertools import ifilter, izip_longest, izip
# from itertools import filter, zip_longest, zip

# Py3 compatibility hack
from itertools import zip_longest
ifilter = filter
izip_longest = zip_longest
izip = zip

from collections import OrderedDict


def generate_method_key(method):
    """
        Generate an hashable key for a given method.
        In more details, for a given method, the key is
        represented by a tuple corresponding to:
            (class name, method name, type names of all parameters)
    """

    class_name = method.code_class.class_name
    method_name = method.method_name

    try:
        # Get type names
        parser = etree.XMLParser(recover=True)  # recover from bad characters.
        xml_tree = etree.fromstring(method.xml_tree, parser=parser)
        # doc = etree.ElementTree(xml_tree)
        # Extract Nodes corresponding to Types of FORMAL PARAMETER(s)
        xpath_query = '//method_statement_node/node[@instruction_class="FORMAL_PARAMETERS"]/' \
                      'node[@instruction_class="FORMAL_PARAMETER"]/node[@instruction_class="TYPE"]'
        parameter_type_nodes = xml_tree.xpath(xpath_query)
    except etree.XMLSyntaxError as exc:
        print('XML Syntax Error Found!!', exc.msg)
        print('Method: ', method_name)
        exit()
    else:
        type_names = list()
        for node in parameter_type_nodes:
            type_names.append(node.attrib['name'])
        key = [class_name, method_name]
        key.extend(type_names)
        return tuple(key)  # Finally convert the key list to a tuple (immutable)


def index_methods_of_projects(software_project):
    """
        Extract all the methods from a given software projects.
        Returned methods are indexed by the corresponding key
        (see method `generate_method_key`)

        Parameters:
        -----------
            software_project: SoftwareProject
                The instance of the SoftwareProject where methods have to be gathered from.

        Returns:
        --------
            methods: dict
                A dictionary mapping each method instance to their corresponding key.
    """

    code_methods = software_project.code_methods.all()  # Get all methods of the Sw Project
    indexed_methods = dict()

    for method in code_methods:
        key = generate_method_key(method)
        indexed_methods[key] = method
    return indexed_methods


def similarity_of_comments(method1, method2):
    """
    Compute the similarity of Head Comments of
    given methods.
    Comments similarity is computed by the Hamming Distance
    between the words of the comments (excluding
    punctuations, and formattings) represented as a
    big joint string.
    """

    def normalize_comment(comment):
        tokens = wordpunct_tokenize(comment)
        tokens = ifilter(unicode.isalnum, tokens)
        return ''.join(tokens).lower()

    def hamming_distance(s1, s2):
        """Return the Hamming distance between any-length sequences of characters"""
        return sum(ch1 != ch2 for ch1, ch2 in izip_longest(s1, s2, fillvalue=''))

    comment1 = normalize_comment(method1.comment)
    comment2 = normalize_comment(method2.comment)
    length = max(len(comment1), len(comment2))
    if not length:
        return 1
    hd = hamming_distance(comment1, comment2)
    return 1 - (hd/length)


def similarity_of_code(method1, method2):
    """
    Compute the similarity of Code Fragments of the two given methods
    using the (Tree) Kernel Functions among corresponding
    Code Fragment (i.e., XML Parse Tree Fragments associated to each method
    during the Code Parsing/Analysis phase)
    """

    method1_xml_tree = '\n'.join([ParsedTreeNode.from_unicode_to_xml(line) for line in
                                  method1.xml_tree.splitlines()])
    method2_xml_tree = '\n'.join([ParsedTreeNode.from_unicode_to_xml(line) for line in
                                  method2.xml_tree.splitlines()])

    method1_xml_tree = method1_xml_tree.encode('utf-8')
    method2_xml_tree = method2_xml_tree.encode('utf-8')

    try:
        parse_tree1 = XMLMethodTreeParser().parse(method1_xml_tree)
        parse_tree2 = XMLMethodTreeParser().parse(method2_xml_tree)
    except ExpatError:
        return -1
    except UnicodeEncodeError:
        return -1
    else:
        return contiguous_tree_kernel(parse_tree1, parse_tree2)


def get_common_methods(methods_release, methods_next_release):
    """
        Find and returns all the methods that are present in
        both the lists of methods, corresponding to two different
        releases of the *same* software project.

        Parameters:
        -----------
            methods_release: dict
                A dictionary containing all the methods of the first project
                release, as returned by the `index_methods_of_projects`
                function.

            methods_next_release: dict
                A dictionary containing all the methods of the second project
                release, as returned by the `index_methods_of_projects`
                function.

        Return:
        -------
            methods_in_common: dict
                A dictionary containing the references to only the
                common methods between the two considered releases.
                Selected methods are only those that differ at least in one
                between comment and code.
                The resulting dictionary contains for each couple of methods, the
                values of code and comment similarities (as computed by the
                `similarity_of_code` and `similarity_of_comments` functions).
    """

    methods_in_common = dict()
    for mkey in methods_release:
        if mkey in methods_next_release:

            # Before setting the Common Method, check if something **actually** changed.

            method_current_release = methods_release[mkey]
            method_next_release = methods_next_release[mkey]

            # Getting Comment Similarity
            comment_sim = similarity_of_comments(method_current_release, method_next_release)
            # Getting Code Similarity
            code_sim = similarity_of_code(method_current_release, method_next_release)

            if (0 <= comment_sim < 1) or (0 <= code_sim < 1):
                methods_in_common.setdefault(mkey, dict())
                methods_in_common[mkey].setdefault('methods', list())
                methods_in_common[mkey]['methods'].append(method_current_release)
                methods_in_common[mkey]['methods'].append(method_next_release)
                methods_in_common[mkey]['code_similarity'] = code_sim
                methods_in_common[mkey]['comment_similarity'] = comment_sim

    return methods_in_common  # return only common methods


def generate_excel_report_file(target_methods, system_names=(), filename='methods_report.xlsx'):
    """
        Generate an XLS(X) - Excel - Report file containing all
        the information to compare and evaluate target methods.
        In particular, this report aims at producing an output
        suitable to compare two versions of the **same** methods
        within two different (consecutive) software releases.

        The Excel report file is generated thanks to the
        [`xlsxwriter`](https://xlsxwriter.readthedocs.org/)
        Python library.

        Arguments:
        ----------
            target_methods: dict
                A dictionary containing all the target methods to compare
                (as returned by the `get_common_methods` function)

            system_names: tuple (default: () - empty tuple)
                A tuple containing the names of the two compared systems (and release numbers).
                If None (default), the two systems will be referred in the report as
                "First Release" and "Second Release", respectively.

            filename: str (default: "methods_report.xlsx")
                The name of the Excel file to generate.
    """

    # Creating The Excel Workbook
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    # Add a format for the header cells.
    header_format = workbook.add_format({
        'border': 1,
        # 'bg_color': '#C6EFCE',
        'bold': True,
        'text_wrap': True,
        'valign': 'vcenter',
        'align': 'center',
        'indent': 1,
    })

    centered_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'bold': True
    })

    # Set up some formats to use.
    bold = workbook.add_format({'bold': True})  # Bold
    center = workbook.add_format({'align': 'center'})  # Center
    # Txt Wrap (for code and comments)
    tx_wrap = workbook.add_format({'valign': 'top', 'align': 'left'})
    tx_wrap.set_text_wrap()
    # Valign Top for Notes
    vtop = workbook.add_format({'valign': 'top', 'align': 'left', 'locked': False})
    # Unlocked
    unlocked = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'bold': True,
        'locked': False
    })

    # Set up layout of the worksheet.
    worksheet.set_column('A:B', 80)
    worksheet.set_column('C:C', 2)
    worksheet.set_column('D:E', 15)
    worksheet.set_column('F:F', 2)
    worksheet.set_column('G:H', 20)
    worksheet.set_column('I:I', 2)
    worksheet.set_column('J:K', 20)
    worksheet.set_column('L:L', 2)
    worksheet.set_column('M:M', 40)

    # Check System Names
    if not system_names or not len(system_names):
        system_names = ('First Release', 'Second Release')
    if len(system_names) < 2:
        system_names = (system_names[0], 'Second Release')

    # Write the header cells and some data that will be used in the examples.
    heading1 = system_names[0]  # A - 80
    heading2 = system_names[1]  # B - 80
    heading3 = 'Comment Changed'  # D - 15
    heading4 = 'Code Changed'  # E - 15
    heading5 = 'Comment Lexical Similarity'  # G - 20
    heading6 = 'Code Textual Similarity'  # H - 20
    heading7 = 'Are the Comments Semantically Different?'  # J
    heading8 = 'Are the Code Fragments Semantically Different?'  # K
    heading9 = 'Notes'  # M

    # Methods
    worksheet.write('A1', heading1, header_format)
    worksheet.write('B1', heading2, header_format)

    # Code and Comment Changed (selection)
    worksheet.write('D1', heading3, header_format)
    worksheet.write('E1', heading4, header_format)

    # Code and Comments Similarity
    worksheet.write('G1', heading5, header_format)
    worksheet.write('H1', heading6, header_format)

    # Code and Comments Semantic Similarity Evaluation
    worksheet.write('J1', heading7, header_format)
    worksheet.write('K1', heading8, header_format)

    # Notes
    worksheet.write('M1', heading9, header_format)

    def write_method_code_fragment(method, location):
        """Utility Closure to write Code fragment of given method at a specified location"""
        code_fragment = method.code_fragment
        open_brackets_count = code_fragment.count('{')
        closed_brackets_count = code_fragment.count('}')
        if open_brackets_count != closed_brackets_count:
            code_fragment += '}' * (open_brackets_count - closed_brackets_count)
        lines = method.comment.splitlines()
        lines.extend(code_fragment.splitlines())
        lines = [l for l in lines if len(l.strip())]
        fragment = '\n'.join(lines)
        worksheet.write(location, fragment, tx_wrap)
        return fragment

    def write_validation_list_and_preselect(similarity, location, semantic_difference=False):
        if 0 <= similarity <= 1:
            if 0 <= similarity < 1:
                if not semantic_difference:  # default
                    # In this case, the column to write does not refer to the semantic
                    # equivalence, but to the lexical similarity
                    worksheet.write(location, 'YES', unlocked)
            else:
                worksheet.write(location, 'NO', unlocked)
        else:
            worksheet.write(location, '', unlocked)
        worksheet.data_validation(location,
                                  {'validate': 'list', 'source': ['YES', 'NO']})

    # Start writing the Excel File
    row_counter = 2
    for mkey in sorted(target_methods.keys()):
        # Get Methods
        method1, method2 = target_methods[mkey]['methods']
        code_similarity = target_methods[mkey]['code_similarity']
        comment_similarity = target_methods[mkey]['comment_similarity']

        # Write Method Information
        worksheet.write_rich_string('A{r}'.format(r=row_counter),
                                    bold, 'Method: ', method1.method_name,
                                    ' (Class: {0})'.format(method1.code_class.class_name), center)
        worksheet.write_rich_string('B{r}'.format(r=row_counter),
                                    bold, 'Method: ', method2.method_name,
                                    ' (Class: {0})'.format(method2.code_class.class_name), center)

        # Write Method Comment and Code
        row_counter += 1

        fragment1 = write_method_code_fragment(method1, 'A{r}'.format(r=row_counter))
        fragment2 = write_method_code_fragment(method2, 'B{r}'.format(r=row_counter))
        # Set row Height to the Largest row
        worksheet.set_row(row_counter, 0.15*(max(len(fragment1), len(fragment2))))

        # Write Selection List for Code and Comment Lexical/Textual Changes
        write_validation_list_and_preselect(comment_similarity, 'D{r}'.format(r=row_counter))
        write_validation_list_and_preselect(code_similarity, 'E{r}'.format(r=row_counter))

        # Write Code and Comment Similarity
        worksheet.write('G{r}'.format(r=row_counter), '%.3f' % comment_similarity, centered_format)
        worksheet.write('H{r}'.format(r=row_counter), '%.3f' % code_similarity, centered_format)

        # Write Selection List for Code and Comment Semantic Changes
        write_validation_list_and_preselect(comment_similarity, 'J{r}'.format(r=row_counter),
                                            semantic_difference=True)
        write_validation_list_and_preselect(code_similarity, 'K{r}'.format(r=row_counter),
                                            semantic_difference=True)

        # Set Notes Format
        worksheet.write('M{r}'.format(r=row_counter), '', vtop)

        # Increment Row Counter by two
        row_counter += 2

    # Turn worksheet protection on.
    # worksheet.protect()

if __name__ == '__main__':

    # Get JHotDraw Systems sorted by Versions
    jhotDraw_systems = SoftwareProject.objects.filter(name__iexact='JHotDraw').order_by('version')

    print('Indexing Methods of Target Systems')
    jhd_methods = OrderedDict()  # Using Ordered Dict to insert keys already sorted by version no.
    for jhd_system in jhotDraw_systems:
        methods = index_methods_of_projects(jhd_system)
        print('Found ', len(methods), ' Methods in JHotDraw ', jhd_system.version)
        jhd_methods[jhd_system.version] = methods

    print('Extracting Common Methods from successive releases')

    for current_release, next_release in izip(jhd_methods.keys()[:-1], jhd_methods.keys()[1:]):

        print('Getting Common Methods From JHotDraw Releases: ',
              current_release, ' - ', next_release)

        current_release_methods = jhd_methods[current_release]
        next_release_methods = jhd_methods[next_release]

        # Extract Common Methods
        common_methods = get_common_methods(current_release_methods, next_release_methods)
        print('Found ', len(common_methods), ' Common Methods between the two releases!')

        if len(common_methods):
            print('Generating Report File')
            # Generate Report File
            report_filename = 'methods_report_JHotDraw_{0}_{1}.xlsx'.format(current_release,
                                                                            next_release)
            generate_excel_report_file(common_methods,
                                       filename=report_filename,
                                       system_names=('JHotDraw {0}'.format(current_release),
                                                     'JHotDraw {0}'.format(next_release)))
            print('Done')