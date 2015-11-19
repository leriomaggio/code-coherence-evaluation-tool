"""
:Author: Valerio Maggio
:Organization: University of Naples Federico II
:Contact: valerio.maggio@unina.it

"""

# Celery Tasks will be added here.

from collections import defaultdict

from celery import task
from .code_analysis.utils import get_sources_from_dir
from .code_analysis.analyzers import analyzers_map

# Import Code Analysis models
from .models import CodeClass, CodeMethod, SourceCodeFile
from .settings import FILES_PER_TASK

from django.conf import settings

import os

# Define the task to generate `SourceCodeFile` entity models
@task()
def create_source_code_file_task(project, filepath):
    """
    Callback function/celery task to instantiate a `SourceCodeFile` entity
    model after the source code archive associated to `project` has been
    correctly extracted.
    """
    if os.path.exists(filepath):
        with open(filepath) as src_file:
            text_content = ''
            relative_filepath = filepath.replace(settings.MEDIA_ROOT, '')  #relative path
            if relative_filepath.startswith(os.path.sep):
                relative_filepath = relative_filepath[1:]
            for line in src_file:
                text_content += line
            src_code_file = SourceCodeFile()
            src_code_file.project= project
            src_code_file.filepath = relative_filepath
            src_code_file.source_code_text = text_content
            src_code_file.save()

# Define the analysis only task
@task()
def analysis_task(code_analyzer_cls, task_item):
    """Callback function for the Task *Analysis*"""

    source_files_list = task_item.source_files_list
    code_analyzer = code_analyzer_cls(source_files_list,
                                      task_item.src_folder_path,
                                      task_item.xml_destination_folderpath)

    code_analyzer.parse_code_files()


@task()
def mapping_task(code_analyzer_cls, task_item):
    """Celery Task to generate a Project Code Base"""
    # Step 1: Code Analysis
    code_analyzer = code_analyzer_cls(task_item.source_files_list,
                                      task_item.src_folder_path,
                                      task_item.xml_destination_folderpath)

    code_analyzer.map_code_and_comments()
    association_map = code_analyzer.method_comments_map

    # Step 2: Store data into the DB
    sw_project = task_item.software_project
    for meth_comment_map_obj in association_map:
        # Get the Class ParsedTreeNode
        class_node = meth_comment_map_obj.class_node

        # Code Class
        code_class = CodeClass()
        code_class.class_name = class_node.code_label
        code_class.start_line = class_node.startline
        code_class.end_line = class_node.endline
        code_class.file_path = class_node.src_relative_filepath

        code_class.xml_tree = class_node.repr_in_xml()
        code_class.project = sw_project

        if meth_comment_map_obj.class_comment:
            code_class.comment = meth_comment_map_obj.class_comment.getText()
        else:
            code_class.comment = ""
        code_class.save()

        # Get the Methods-Comments Map
        meths_comments_map = meth_comment_map_obj.methods_comments_map
        for method_node, comments in meths_comments_map.iteritems():
            code_method = CodeMethod()
            # Reference Info
            code_method.project = sw_project
            code_method.code_class = code_class

            code_method.method_name = method_node.code_label
            code_method.start_line = method_node.startline
            code_method.end_line = method_node.endline
            code_method.file_path = method_node.src_relative_filepath

            code_method.xml_tree = method_node.repr_in_xml()
            if comments and len(comments):
                if len(comments) > 1:
                    separation_mark = '\n --------------\n'
                else:
                    separation_mark = ''
                comment_text = ''
                for comment in comments:
                    comment_text += comment.getText() + separation_mark
                code_method.comment = comment_text
            else:
                code_method.comment = ""

            code_method.save()

#=========================
# Utils for Code Analysis
#=========================


class TaskItem(object):
    """
    A single item to be processed by a single working Thread.
    """

    def __init__(self, project, extension, xml_dest_folder_path, files_list):
        self._src_folder = project.source_folder_path
        self._xml_dest_folder = xml_dest_folder_path
        self._source_files_list = files_list
        self._code_extension = extension
        self._target_project = project

    @property
    def src_folder_path(self):
        return self._src_folder

    @property
    def xml_destination_folderpath(self):
        return self._xml_dest_folder

    @property
    def source_files_list(self):
        return self._source_files_list

    @property
    def code_extension(self):
        return self._code_extension

    @property
    def software_project(self):
        return self._target_project


def generate_task_data(project, xml_folder_path, files_per_task=FILES_PER_TASK):
    """
    Start the analysis task as a whole, instantiating Thread Pools.

    Parameters
    ----------

    project : The `SoftwareProject` instance to associate analysed `CodeArtifacts`

    xml_folder_path : The path to the folder containing XML files, namely the XML
                      representation of the AST generated right after the source
                      code parsing step.

    files_per_task : The total number of source files to process for each task.
    """

    # Get Source Code Files (paths)
    source_code_files = defaultdict(list)
    tot_source_files = 0

    # The `file_extensions` as a list is useful in many cases and makes the whole
    # processing more flexible. In particular, the list allows for multiple
    # source file extensions for the same language (e.g., C++ with .cpp, .cc)
    # and/or for multi-language parsing.
    extensions_list = project.file_extensions.split(';')

    for extension in extensions_list:
        source_code_files[extension] = get_sources_from_dir(project.source_folder_path, extension)
        tot_source_files += len(source_code_files[extension])

    # Different extensions may lead to different Code Analyzers. Thus create Pools
    # of Threads for each extension in `file_extentions`

    for extension in extensions_list:
        # Get the proper Analyzer Class according to the extension
        code_analyzer_cls = analyzers_map[extension]
        # Get code filepaths list based on the extension
        code_file_paths = source_code_files[extension]

        # Now generate TaskItems grouping source files paths in groups of
        # `files_per_task` number of elements.
        start = 0
        while True:
            end = start + files_per_task
            if end > len(code_file_paths):
                end = len(code_file_paths)
            item = TaskItem(project, extension, xml_folder_path, code_file_paths[start:end])
            yield (code_analyzer_cls, item)

            # Update the "new" start for the next iteration count
            start = end

            # After having added the request check the value of `end` to
            # know if its time to break the loop
            if end >= len(code_file_paths):
                break