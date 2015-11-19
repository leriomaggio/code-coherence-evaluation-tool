
from __future__ import division, absolute_import

#-------------------------
# Django framework imports
#-------------------------
from django.contrib import admin
from django.core import urlresolvers
from django.conf import settings
from django.contrib.messages import ERROR
from django.utils.translation import gettext_lazy as _

from django.http import HttpResponse, HttpResponseNotModified, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.conf.urls import patterns, url

#-------------------------
# Project specific imports
#-------------------------
from .models import SoftwareProject, CodeClass, CodeMethod, AgreementEvaluation, SourceCodeFile
from .models import AgreementEvaluationToBeChecked
from .forms import SoftwareProjectAdminForm, CodeArtifactAdminForm, SourceCodeFileAdminForm
from .forms import InlineCodeArtifactAdminForm, AgreementEvaluationAdminForm
from .forms import AdminFilterSoftwareProject, AdminFilterCodeClass
from .forms import AdminFilterEvaluated, AdminFilterEvaluator, AdminFilterAgreementVote
from .forms import CodeArtifactModifyAdminForm
from .settings import STRONG_DISAGREEMENT, DISAGREEMENT, DONT_KNOW, AGREEMENT, STRONG_AGREEMENT
from .settings import DEFAULT_AGREEMENT, DEFAULT_AGREEMENT_LABEL
from .settings import FURTHER_EVAL
from .code_analysis.utils import ensure_xml_files_folder

#---------------------
# Celery tasks imports
#---------------------
from .tasks import generate_task_data
from .tasks import create_source_code_file_task
from .tasks import analysis_task, mapping_task
from celery import group

#----------------------
# Python STD Lib Import
#----------------------
from datetime import datetime
import os


class SoftwareProjectAdmin(admin.ModelAdmin):
    form = SoftwareProjectAdminForm
    list_display = ['__str__', 'display_project_url', 'statistics']

    # This is automatically switched to default in case of SUPERUSER Admin
    # see: `render_change_form` method.
    change_form_template = 'admin/change_form_no_save.html'

    #====================
    # Model Admin actions
    #====================

    actions = ['generate_code_base', 'generate_code_files']

    def generate_code_base(self, request, queryset):
        """Admin Action to start the "code-comments" association task to generate the
        code bases of selected projects.

        Please note that any existing code base associated to the project will be deleted and
        freshly re-generated as well.
        """
        rows_updated = 0
        selection_errors = 0
        for sw_project in queryset:
            if sw_project.has_code_base:
                    # Delete the existing Code Base
                    for code_method in sw_project.code_methods.all():
                        code_method.delete()
                    for code_class in sw_project.code_classes.all():
                        code_class.delete()
            xml_folder_path, res = ensure_xml_files_folder(sw_project.source_folder_path)

            # Group Celery Tasks and start them asynchronously
            cb_group = group(mapping_task.s(analyzer_cls, titem) for analyzer_cls, titem in
                             generate_task_data(sw_project, xml_folder_path))
            cb_group.apply_async()
            rows_updated += 1
        # Check positive cases
        if rows_updated:
            if rows_updated == 1:
                msg = _("The generation of the code base of 1 Project has been started and will be \
                        completed shortly. Please hold on a few minutes and refresh this page to \
                        check for updates.")
            else:
                msg = _("The generation of the code base of %d Projects have been started and \
                        will be completed shortly. Please hold on a few minutes and \
                        refresh this page to check for updates.")
            self.message_user(request, msg)

        # Check possible selection error(s)
        if selection_errors:
            if selection_errors == 1:
                message_bit = _("1 selected Software Project has")
            else:
                message_bit = _("%d selected Software Projects have")
            self.message_user(request, _("%s been ignored since the corresponding Code Base \
                                         was not empty!" % message_bit, ERROR))

    generate_code_base.short_description = _("Generate Code Base")

    def apply_async_create_source_code_file_tasks(self, sw_project):
        """ Asynchronously create `SourceCodeFile` instances for the input `SoftwareProject`
        object.
        Asynchrounous tasks are made available through Celery

        Parameters:
        -----------
        sw_project: `SoftwareProject` instance to whom generated `SourceCodeFile` objects are
                    being associated.
        """
        for root, dirnames, filenames in os.walk(sw_project.source_folder_path):
            for filename in filenames:
                if not filename.startswith('.'):  # If this is not an Hidden File
                    src_filepath = os.path.join(root, filename)
                    name, ext = os.path.splitext(src_filepath)
                    if ext and ext in sw_project.file_extensions:
                        create_source_code_file_task.delay(sw_project, src_filepath)
    #
    def generate_code_files(self, request, queryset):
        """ Admin Action to generate `SourceCodeFile` instances based on extracted source files
            on the File System (MEDIA_ROOT)

            Please note that any existing SourceCodeFile instances already stored in the db,
            will be deleted and re-generated from scratch.
        """
        rows_updated = 0
        selection_errors = 0
        for sw_project in queryset:
            if sw_project.source_folder_path:
                if sw_project.source_files.count() > 0:
                    # Delete any existing SourceCodeFile instance already saved
                    for code_file in sw_project.source_files.all():
                        code_file.delete()
                self.apply_async_create_source_code_file_tasks(sw_project)
                rows_updated += 1
            else:
                selection_errors += 1  # Selected Project with no decompressed archive

        # Check positive cases
        if rows_updated:
            if rows_updated == 1:
                msg = _("Code Files for 1 Project are being generated. Please hold on a while \
                        and refresh this page to check for updates.")
            else:
                msg = _("Code Files for %d Project are being generated. Please hold on a while \
                        and refresh this page to check for updates.")
            self.message_user(request, msg)

        # Check possible selection error(s)
        if selection_errors:
            if selection_errors == 1:
                message_bit = _("1 selected Software Project has")
            else:
                message_bit = _("%d selected Software Projects have")
            self.message_user(request, _("%s been ignored since the content of corresponding \
                                         decompressed archive has not been found" % message_bit,
                                         ERROR))

    generate_code_files.short_description = _("Fetch Code Files")

    #=================================
    # Model Admin list_display methods
    #=================================

    def statistics(self, object):
        tag = '''<ul>
            <li><b>No. of Code Files :</b> %d</li>
            <li><b>No. of Code Classes :</b> %d</li>
            <li><b>No. of Code Methods :</b> %d</li>
            </ul>''' % (object.source_files.count(), object.code_classes.count(),
                        object.code_methods.count())

        tag += '''
            <a href="./%d/view_stats/" target="_blank" > %s </a>
                ''' % (object.id, _('View Chart'))
        return tag

    statistics.short_description = _('Project Code Base Statistics')
    statistics.allow_tags = True

    def display_project_url(self, object):
        return '<a href="{url}" title="{name}" target="_blank">{url}</a>'.format(
            url=object.project_url, name=str(object))
    display_project_url.short_description = _('Project Website')
    display_project_url.allow_tags = True


    #===============================
    # Model Admin methods overriding
    #===============================

    def get_form(self, request, obj=None, **kwargs):
        """
        Customize the fields of the ModelForm by
        removing the `src_folder_path` field in
        case we this method has been invoked in an
        `add_view()` (namely, `obj == None`)
        """
        self.exclude = []
        self.readonly_fields = []
        if not obj:
            # this means that we are instantiating an unbounded form
            self.exclude.append('src_folder_path')
        else:
            # the form will be bounded, so the field will be read_only
            self.readonly_fields.append('src_folder_path')
        return super(SoftwareProjectAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        TODO: Specify the customization
        """
        super(SoftwareProjectAdmin, self).save_model(request, obj, form, change)

        # start celery analysis tasks
        xml_folder_path, folder_existing = ensure_xml_files_folder(obj.source_folder_path)
        if not folder_existing:
            # Start the parsing task only if the xml_folder_path has been created for the first
            # time invoking the `ensure_xml_files_folder` function
            task_group = group(analysis_task.s(analyzer, task_item) for analyzer, task_item in
                               generate_task_data(obj, xml_folder_path))

            task_group.apply_async()
            msg = _("The code analysis process is now working in background. "
                    "Please check in a few moments")
            self.message_user(request, msg, "INFO")

    def get_actions(self, request):
        usr = request.user
        if usr.is_superuser or (usr.has_perm('add_codeclass') and usr.has_perm('add_codemethod')):
            return super(SoftwareProjectAdmin, self).get_actions(request)
        return None

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """
        This model admin method has been overridden only to automatically restore the
        `change_form_template` in case the current user is a superadmin.
        In the default case, a staff member user (i.e., `is_staff == True`) cannot save
        Project information.
        """
        if request.user.is_superuser:
            self.change_form_template = None
        return super(SoftwareProjectAdmin, self).render_change_form(request, context, add, change,
                                                                    form_url, obj)

    def get_readonly_fields(self, request, obj=None):
        """ If current user is not a SuperUser Admin, all forms fields are marked as "readonly"
         to avoid possible saving errors.

         Note: In addition, the `change_form_template` as well has all the "save" button
         sets disabled (see `render_change_form` overridden method).
        """
        if not request.user.is_superuser:
            self.readonly_fields = ['name', 'version', 'project_url', 'src_folder_path',
                                    'file_extensions', 'src_package_file']
        return super(SoftwareProjectAdmin, self).get_readonly_fields(request, obj)

    def get_urls(self):
        """
        Added two additional view to support Ajax-based actions from the
        change_list to register agreement evaluations.
        """
        urls = super(SoftwareProjectAdmin, self).get_urls()
        my_urls = patterns('',
                           # url(r'^(?P<project_id>\d+)/view_stats/generate_chart/$',
                           #     self.generate_chart_image, name='project_chart'),
                           url(r'^(?P<project_id>\d+)/view_stats/$',
                               self.view_project_stats, name='project_statistics'),
                           )
        return my_urls + urls

    # ================================
    # Model Admin custom view methods
    # =================================

    def view_project_stats(self, request, project_id):
        import matplotlib.pyplot as plt
        import mpld3

        project_instance = get_object_or_404(SoftwareProject, id=project_id)
        barchart_figure = plt.figure(1, figsize=(6, 6))
        xvalues = range(3)  # the x locations for the groups
        width = 0.5  # the width of the bars
        yvalues = [project_instance.source_files.count(),
                   project_instance.code_classes.count(),
                   project_instance.code_methods.count()]

        plt.title(_(u'Software Project Statistics'))
        plt.bar(xvalues, yvalues, width)
        barchart_d3 = mpld3.fig_to_html(barchart_figure)

        # Generate Pie Chart showing distribution of methods among classes
        total_methods_count = project_instance.code_methods.count()
        classes = project_instance.code_classes.all()
        percentage_values = [cl.methods.count()/total_methods_count for cl in classes]
        labels = [cl.class_name for cl in classes]
        piechart_figure = plt.figure(2, figsize=(11,11))
        plt.title(_(u'Distribution of Methods among classes'))

        from numpy.random import random
        color_values = random(total_methods_count)
        jet_cm = plt.get_cmap('jet')
        plt.pie(percentage_values, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90, colors=jet_cm(color_values))
        piechart_d3 = mpld3.fig_to_html(piechart_figure)
        opts = self.model._meta
        return render_to_response('admin/software_project_stats.html',
                                  {'project': project_instance, 'barchart': barchart_d3,
                                   'piechart': piechart_d3,
                                   'opts': opts, 'app_label': self.model._meta.app_label,},
                                  context_instance=RequestContext(request))

    # def generate_chart_image(self, request, project_id):
    #     from matplotlib.pyplot import bar, figure, close
    #     from matplotlib.backends.backend_agg import FigureCanvasAgg
    #     import numpy as np
    #     import mpld3
    #
    #     project_instance = get_object_or_404(SoftwareProject, id=project_id)
    #     figure = figure(1, figsize=(6,6))
    #
    #     ind = np.arange(3)  # the x locations for the groups
    #     width = 0.35  # the width of the bars
    #     xvalues = ind+width
    #     yvalues = [project_instance.source_files.count(),
    #                project_instance.code_classes.count(),
    #                 project_instance.code_methods.count()]
    #
    #     bar(xvalues, yvalues, width)
    #     # title('Raining Hogs and Dogs', bbox={'facecolor': '0.8', 'pad': 5})
    #
    #     canvas = FigureCanvasAgg(figure)
    #     response = HttpResponse(content_type='image/jpg')
    #     canvas.print_jpg(response)
    #     close(figure)
    #     return response


class CodeArtifactAdmin(admin.ModelAdmin):
    list_filter = ['project']

    readonly_fields = ['file_path']

    change_list_template = "admin/change_list_extra_head.html"

    #=================================
    # Model Admin list_display methods
    #=================================

    def offset(self, object):
        return '<span>(%d - %d)<br><strong>%d Lines</strong></span>' % (
            object.start_line, object.end_line, (object.end_line - object.start_line)+1)

    offset.short_description = _('Lines of Code')
    offset.allow_tags = True

    def display_code_fragment(self, object):
        return object.source_code_fragment

    display_code_fragment.short_description = _('Code Fragment')
    display_code_fragment.allow_tags = True

    def display_code_comment(self, object):
        return object.source_code_comment

    display_code_comment.short_description = _('Code Comment')
    display_code_comment.allow_tags = True

    def source_code_file(self, object):
        filepath = object.file_path
        try:
            src_code_file = SourceCodeFile.objects.get(filepath__exact=filepath)
            change_url = urlresolvers.reverse('admin:source_code_analysis_sourcecodefile_change',
                                              args=(src_code_file.id,))
            tag = '<a href="%s#%d" target="_blank" title="Code file for %s method">' \
                  'Code file</a>' % (change_url, object.start_line, object.display_name)
            return tag
        except SourceCodeFile.DoesNotExist:
            return _('<b>Source File not found in the DB</b>')

    source_code_file.short_description = _('Source File')
    source_code_file.allow_tags = True

    #==============================
    # ModelAdmin method overriding
    #==============================

    def get_readonly_fields(self, request, obj=None):
        """ If current user is not a SuperUser Admin, this method adds to the list of
         readonly_fields, `start_line` and `end_line` fields too to make this fields
         unchangable.

         Please note that, in any case, the `change_form` template has been properly
         changed to remove the `submit_row` templatetag
        """
        readonly_fields = super(CodeArtifactAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser and len(readonly_fields):
            readonly_fields.append('start_line')
            readonly_fields.append('end_line')
        return readonly_fields

    class Media:
        css = {
            "all": (settings.STATIC_URL + 'css/pygments.css',)
        }


class InlineCodeMethodAdmin(admin.StackedInline):
    model = CodeMethod

    form = InlineCodeArtifactAdminForm
    readonly_fields = ['method_name', 'project', 'start_line', 'end_line']
    fieldsets = (
        (None, {
            'fields': (('method_name',), ('start_line', 'end_line'), ),
            'classes': ('extrapretty',),
        }),
        (_('Method Code'), {
            'fields': ('code_fragment',),
            'classes': ('collapse',),
        }),
        (_('Method Comment'), {
            'classes': ('collapse',),
            'fields': ('comment',)
        }),
    )

    class Media:
        css = {
            "all": (settings.STATIC_URL + 'css/pygments.css',)
        }


class CodeClassAdmin(CodeArtifactAdmin):
    list_display = ['display_name', 'offset', 'project',
                    'display_code_comment', 'display_methods_count',
                    'source_code_file']
    search_fields = ['class_name']
    list_per_page = 100
    inlines = [InlineCodeMethodAdmin]

    change_form_template = 'admin/change_form_no_save.html'

    form = CodeArtifactAdminForm
    readonly_fields = CodeArtifactAdmin.readonly_fields + ['class_name']
    fieldsets = (
        (None, {
            'fields': ('file_path', 'class_name', ('start_line', 'end_line'), 'project', ),
            'classes': ('extrapretty',),
        }),
        (_('Class Code'), {
            'fields': ('code_fragment',),
            'classes': ('collapse',),
        }),
        (_('Class Comment'), {
            'classes': ('collapse',),
            'fields': ('comment',)
        }),
        # (_('Class Parse Tree (in XML)'), {
        #     'classes': ('collapse',),
        #     'fields': ('xml_tree',)
        # }),
    )

    #=================================
    # Model Admin list_display methods
    #=================================

    def display_name(self, object):
        cname = object.class_name
        filepath = object.src_filename
        tag = '%s<br>@%s' % (cname, filepath)
        return tag

    display_name.short_description = _('Class')
    display_name.allow_tags = True

    def display_methods_count(self, object):
        methods_count = object.methods.count()
        tag = '<b>%s</b>:%d' % (_('Number of Methods'), methods_count)
        return tag

    display_methods_count.short_description = _('Number of Methods')
    display_methods_count.allow_tags = True

    #==============================
    # ModelAdmin method overriding
    #==============================

    def get_actions(self, request):
        if request.user.is_superuser or request.user.has_perm('delete_codeclass'):
            return super(CodeArtifactAdmin, self).get_actions(request)
        else:
            return None

    class Media:
        css = {
            "all": (settings.STATIC_URL + 'css/pygments.css',)
        }


class CodeMethodAdmin(CodeArtifactAdmin):
    list_display = ['display_name', 'offset', 'display_code_fragment', 'display_code_comment',
                    'source_code_file']
    search_fields = ['method_name']
    list_filter = ['project',]
    list_per_page = 10
    readonly_fields = CodeArtifactAdmin.readonly_fields + ['method_name', 'project']
    #form = CodeArtifactAdminForm

    change_form_template = 'admin/change_form_no_save.html'

    fieldsets = (
        (None, {
            'fields': ('file_path', 'method_name', ('start_line', 'end_line'), 'project', ),
            'classes': ('extrapretty',),
        }),
        ('Method Code', {
            'fields': ('code_fragment',),
            # 'classes': ('collapse',),
        }),
        ('Method Comment', {
            # 'classes': ('collapse',),
            'fields': ('comment',)
        }),
        # ('Method Parse Tree (in XML)', {
        #     'classes': ('collapse',),
        #     'fields': ('xml_tree',)
        # }),
    )

    #=================================
    # Model Admin list_display methods
    #=================================

    def display_name(self, object):
        fname = object.method_name
        class_name = object.code_class.src_filename
        tag = '%s<br>@%s' % (fname, class_name)
        return tag

    display_name.short_description = _('Method')
    display_name.allow_tags = True

    #==============================
    # ModelAdmin method overriding
    #==============================

    def get_actions(self, request):
        if request.user.is_superuser or request.user.has_perm('delete_codemethod'):
            return super(CodeArtifactAdmin, self).get_actions(request)
        else:
            return None

    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            self.form = CodeArtifactModifyAdminForm
        else:
            self.form = CodeArtifactAdminForm
        return super(CodeMethodAdmin, self).get_form(request, obj, **kwargs)

    class Media:
        css = {
            "all": (settings.STATIC_URL + 'css/pygments.css',)
        }


class AgreementEvaluationAdmin(admin.ModelAdmin):
    list_display = ['code_fragment', 'comment', 'agreement_voting']
    list_filter = ['evaluated','reference_method__project',
                   'reference_method__code_class', 'evaluator',
                   'agreement_vote',]

    search_fields = ['reference_method__method_name', ]
    list_per_page = 100

    change_list_template = "admin/change_list_filters_on_top.html"

    form = AgreementEvaluationAdminForm
    readonly_fields = ['evaluator', 'evaluation_datetime', 'last_update']

    fieldsets = (
        (_('Code-Comments Evaluation'), {
            'fields': (('code_fragment', 'code_comment'),
                       ('agreement_vote', 'wrong_association'),
                       ('evaluation_datetime', 'last_update')),
        }),
        (_('Method Information'), {
            'fields': (('method_name', 'start_line', 'end_line',),),
            'classes': ('collapse',),
        }),
    )

    #=================================
    # Model Admin list_display methods
    #=================================

    def code_fragment(self, object):
        return object.reference_method.source_code_fragment

    code_fragment.short_description = _("Code Fragment")
    code_fragment.allow_tags = True

    def comment(self, object):
        return object.reference_method.source_code_comment

    comment.short_description = _("Comment")
    comment.allow_tags = True

    def _code_file_info(self, object):
        try:
            filepath = object.reference_method.file_path
            src_code_file = SourceCodeFile.objects.get(filepath__exact=filepath)
            change_url = urlresolvers.reverse('admin:source_code_analysis_sourcecodefile_change',
                                              args=(src_code_file.id,))

            msg = _('Are you not sure enough? <br><br> Please take a look at the ')
            msg_title = _('Code file for %s method' % object.reference_method.display_name)
            link_label = _('for the method ')
            addendum = '''
                        <br><br>
                        <p>
                            <span>{message}</span>
                            <a href="{change_url}#{start_line}" target="_blank"
                               title="{link_title}">
                            Code file </a>
                            {link_label}
                            <span style="font-family: Courier New, Arial, sans-serif;">
                                {method_name}
                            </span>
                        </p>'''.format(message=msg, change_url=change_url, link_title=msg_title,
                                       start_line=object.reference_method.start_line,
                                       link_label=link_label,
                                       method_name=object.reference_method.display_name)
        except SourceCodeFile.DoesNotExist:
            addendum = ''
        evaluation_question = _('What is the agreement rate between this Comment and \
                                corresponding Method code?')
        return addendum, evaluation_question

    def _agreement_vote_widget(self, addendum, evaluation_question, object):

        target_field = object._meta.fields[3]  # should be 'wrong_association'
        label_value = target_field.verbose_name if target_field.name == 'wrong_association' else \
            _('Error in Association')

        selected_keys = {
            'question_message': evaluation_question,
            'obid': str(object.id), 'stdis': STRONG_DISAGREEMENT, 'dis': DISAGREEMENT,
            'dk': DONT_KNOW, 'agr': AGREEMENT, 'stagr': STRONG_AGREEMENT,
            'label': label_value, 'addendum': addendum, 'default': DEFAULT_AGREEMENT_LABEL,
            'id_-1': '', 'id_0': '', 'id_1': '', 'id_2': '', 'id_3': '', 'id_4': '',
            'checked': 'checked' if object.wrong_association else ''}

        if object.agreement_vote != DEFAULT_AGREEMENT:
            selected_keys.update({'id_' + str(object.agreement_vote): 'selected="selected"'})
        else:
            selected_keys.update({'id_-1': 'selected="selected"'})

        # TODO: This could be easily fixed with a Django Form Instance (maybe)
        tag = '''<div class="agreement_rate">
                <p>
                {question_message}
                </p>
                <select id="id_agreement_vote-{obid}" name="{obid}">
                    <option value="-1" {id_-1}>{default}</option>
                    <option value="0" {id_0}>{stdis}</option>
                    <option value="1" {id_1}>{dis}</option>
                    <option value="2" {id_2}>{dk}</option>
                    <option value="3" {id_3}>{agr}</option>
                    <option value="4" {id_4}>{stagr}</option>
                </select>
                <br>
                <br>
                <label for="id_form-wrong_association-{obid}"><b>{label}:</b></label>
                <input id="id_form-wrong_association-{obid}" name="wrong_association-{obid}"
                        type="checkbox" {checked}>
                <br>
                {addendum}
                </div>
                '''.format(**selected_keys)
        return tag

    def agreement_voting(self, object):
        """
        This method shows ...
        """
        #TODO Complete Method doc
        addendum, evaluation_question = self._code_file_info(object)
        return self._agreement_vote_widget(addendum, evaluation_question, object)

    agreement_voting.short_description = _('Agreement')
    agreement_voting.allow_tags = True

    #===============================
    # Model Admin methods overriding
    #===============================

    def queryset(self, request):
        """
        This method returns different `AgreementEvaluation` queryset depending on the
        priviegies of `request.user`.
        In case, `request.user` is a superuser, this method has the default behaviour.
        Otherwise, this method returns the set of AgreementEvaluations filtered by current
        evaluator.

        (This documentation may be improved)
        """

        if request.user.is_superuser:
            return super(AgreementEvaluationAdmin, self).queryset(request)

        request_user = request.user
        return request_user.evaluations.exclude(agreement_vote=5)  # Use RelatedManager

    def get_actions(self, request):
        """If the current user is not a Superuser, no action will be allowed"""
        if request.user.is_superuser or request.user.has_perm('delete_agreementevaluation'):
            return super(AgreementEvaluationAdmin, self).get_actions(request)
        else:
            return None

    def get_urls(self):
        """
        Added two additional view to support Ajax-based actions from the
        change_list to register agreement evaluations.
        """
        urls = super(AgreementEvaluationAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^(?P<evaluation_id>\d+)/agreement/$',
                               self.change_agreement_evaluation, name='ajax_change_evaluation'),
                           url(r'^(?P<evaluation_id>\d+)/wrong-association/$',
                               self.mark_wrong_association, name='ajax_mark_wrong_association'),
        )
        return my_urls + urls

    def changelist_view(self, request, extra_context=None):
        """
        """
        q = request.GET.copy()

        # Remove Empty values to avoid errors in search (queries)
        if 'reference_method__project' in q and q['reference_method__project'] == '':
            q.pop('reference_method__project')

        if 'reference_method__code_class' in q and q['reference_method__code_class']== '':
            q.pop('reference_method__code_class')

        if 'evaluated' in q and q['evaluated'] == '':
            q.pop('evaluated')

        if 'evaluator' in q and q['evaluator'] == '':
            q.pop('evaluator')

        if 'agreement_vote' in q and q['agreement_vote'] == '':
            q.pop('agreement_vote')

        request.GET = q
        request.META['QUERY_STRING'] = request.GET.urlencode()

        # Set `filter_formset`
        filter_formset = list()

        # Check if this filters make sense:
        # If only one instance of Project and/or Class is stored in the DB, the filter
        # does not make any sense! :)
        if SoftwareProject.objects.count() > 1:
            filter_formset.append(AdminFilterSoftwareProject(request))
        if CodeClass.objects.count() > 1:
            filter_formset.append(AdminFilterCodeClass(request))
        filter_formset.append(AdminFilterEvaluated(request))
        filter_formset.append(AdminFilterAgreementVote(request))

        # At last, add the filter based on evaluators in case current user is a superuser
        if request.user.is_superuser:
            filter_formset.append(AdminFilterEvaluator(request))

        new_context = {'filter_formset': filter_formset}
        new_context.update(extra_context or {})
        return super(AgreementEvaluationAdmin, self).changelist_view(request,
                                                                     extra_context=new_context)

    #================================
    # Model Admin custom view methods
    #================================

    def change_agreement_evaluation(self, request, evaluation_id):
        """
        TODO
        """
        # TODO: Complete Documentation

        if request.is_ajax and request.method == 'POST' and request.user.is_staff:
            agreement_rate = int(request.POST.get('evaluation', None))
            if agreement_rate is None:
                return HttpResponseBadRequest(content='KO')

            agreement_eval = get_object_or_404(AgreementEvaluation, pk=evaluation_id)
            if agreement_eval.agreement_vote != agreement_rate:

                agreement_eval.agreement_vote = agreement_rate
                update_fields = ['agreement_vote']

                if agreement_rate != DEFAULT_AGREEMENT:
                    agreement_eval.evaluation_datetime = datetime.now()
                    update_fields.append('evaluation_datetime')

                agreement_eval.save(update_fields=update_fields)
                return HttpResponse(content='OK')
            return HttpResponseNotModified()
        return HttpResponseBadRequest(content='KO')

    def mark_wrong_association(self, request, evaluation_id):
        """
        TODO
        """
        # TODO: Complete Documentation
        if request.is_ajax and request.method == 'POST' and request.user.is_staff:
            wrong_association_value = request.POST.get('wrong', None)
            if wrong_association_value is None:
                return HttpResponseBadRequest(content='KO')
            wrong_association_value = bool(int(wrong_association_value))
            agreement_eval = get_object_or_404(AgreementEvaluation, pk=evaluation_id)

            if agreement_eval.wrong_association != wrong_association_value:
                agreement_eval.wrong_association = wrong_association_value
                agreement_eval.agreement_vote = DEFAULT_AGREEMENT
                agreement_eval.evaluation_datetime = datetime.now()

                agreement_eval.save(update_fields=['agreement_vote', 'evaluation_datetime',
                                                   'wrong_association'])
                return HttpResponse(content='OK')
            return HttpResponseNotModified()
        return HttpResponseBadRequest(content='KO')

    class Media:
        css = {
            "all": (settings.STATIC_URL + 'css/pygments.css',)
        }

        js = [
            settings.STATIC_URL + 'js/admin_agreement_eval.js',
        ]

class AgreementEvaluationToBeCheckedAdmin(AgreementEvaluationAdmin):
    """
    Specialized Version of the `AgreementEvaluationAdmin` Class which
    is specifically suited to evaluate "To be checked" `AgreementEvaluation`
    instances.
    """

    list_filter = ['reference_method__project', 'reference_method__code_class', 'evaluator',]

    def _agreement_vote_widget(self, addendum, evaluation_question, object):
        target_field = object._meta.fields[3]  # should be 'wrong_association'
        label_value = target_field.verbose_name if target_field.name == 'wrong_association' else \
            _('Error in Association')

        selected_keys = {
            'question_message': evaluation_question,
            'obid': str(object.id), 'stdis': STRONG_DISAGREEMENT, 'dis': DISAGREEMENT,
            'dk': DONT_KNOW, 'agr': AGREEMENT, 'stagr': STRONG_AGREEMENT,
            'label': label_value, 'addendum': addendum, 'default': DEFAULT_AGREEMENT_LABEL,
            'sttbc': FURTHER_EVAL,
            'id_-1': '', 'id_0': '', 'id_1': '', 'id_2': '', 'id_3': '', 'id_4': '',
            'checked': 'checked' if object.wrong_association else ''}

        if object.agreement_vote != DEFAULT_AGREEMENT:
            selected_keys.update({'id_' + str(object.agreement_vote): 'selected="selected"'})
        else:
            selected_keys.update({'id_-1': 'selected="selected"'})

        # TODO: This could be easily fixed with a Django Form Instance (maybe)
        tag = '''<div class="agreement_rate">
                    <p>
                    {question_message}
                    </p>
                    <select id="id_agreement_vote-{obid}" name="{obid}">
                        <option value="-1" {id_-1}>{default}</option>
                        <option value="0" {id_0}>{stdis}</option>
                        <option value="1" {id_1}>{dis}</option>
                        <option value="2" {id_2}>{dk}</option>
                        <option value="3" {id_3}>{agr}</option>
                        <option value="4" {id_4}>{stagr}</option>
                        <option value="5" {id_5}>{sttbc}</option>
                    </select>
                    <br>
                    <br>
                    <label for="id_form-wrong_association-{obid}"><b>{label}:</b></label>
                    <input id="id_form-wrong_association-{obid}" name="wrong_association-{obid}"
                            type="checkbox" {checked}>
                    <br>
                    {addendum}
                    </div>
                    '''.format(**selected_keys)
        return tag

    # ===============================
    # Model Admin methods overriding
    #===============================

    def queryset(self, request):
        if request.user.is_superuser:
            qs = AgreementEvaluation.objects.all()
        else:
            qs = request.user.evaluations.all()
        return qs.filter(agreement_vote=5)

    def changelist_view(self, request, extra_context=None):
        """
        """
        q = request.GET.copy()

        # Remove Empty values to avoid errors in search (queries)
        if 'reference_method__project' in q and q['reference_method__project'] == '':
            q.pop('reference_method__project')

        if 'reference_method__code_class' in q and q['reference_method__code_class'] == '':
            q.pop('reference_method__code_class')

        if 'evaluator' in q and q['evaluator'] == '':
            q.pop('evaluator')

        request.GET = q
        request.META['QUERY_STRING'] = request.GET.urlencode()

        # Set `filter_formset`
        filter_formset = list()

        # Check if this filters make sense:
        # If only one instance of Project and/or Class is stored in the DB, the filter
        # does not make any sense! :)
        if SoftwareProject.objects.count() > 1:
            filter_formset.append(AdminFilterSoftwareProject(request))
        if CodeClass.objects.count() > 1:
            filter_formset.append(AdminFilterCodeClass(request))

        # At last, add the filter based on evaluators in case current user is a superuser
        if request.user.is_superuser:
            filter_formset.append(AdminFilterEvaluator(request))

        new_context = {'filter_formset': filter_formset}
        new_context.update(extra_context or {})
        return super(AgreementEvaluationToBeCheckedAdmin, self).changelist_view(request,
                                                                     extra_context=new_context)


class SourceCodeFileAdmin(admin.ModelAdmin):
    readonly_fields = ['filepath']
    exclude = ['project', 'filepath']
    list_display = ['filepath', 'project']
    list_filter = ['project']
    form = SourceCodeFileAdminForm
    change_form_template = 'admin/change_form_no_save.html'

    class Media:
        css = {
            "all": (settings.STATIC_URL + 'css/pygments.css',)
        }


admin.site.register(SoftwareProject, SoftwareProjectAdmin)
admin.site.register(CodeClass, CodeClassAdmin)
admin.site.register(CodeMethod, CodeMethodAdmin)
admin.site.register(AgreementEvaluation, AgreementEvaluationAdmin)
admin.site.register(SourceCodeFile, SourceCodeFileAdmin)
admin.site.register(AgreementEvaluationToBeChecked, AgreementEvaluationToBeCheckedAdmin)