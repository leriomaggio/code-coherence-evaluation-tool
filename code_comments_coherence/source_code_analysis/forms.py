"""
:Author: Valerio Maggio
:Organization: University of Naples Federico II
:Contact: valerio.maggio@unina.it

"""

from .models import AgreementEvaluation, SoftwareProject, CodeClass
from .settings import ACCEPTED_MIMETYPES, AGREEMENT_RATES
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import mimetypes  # This is used in the `SoftwareProjectAdminForm.clean_src_package_file`

from django.utils.html import format_html, mark_safe
from django.forms.util import flatatt
from django.contrib.auth.models import User

from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.lexers.compiled import JavaLexer
from pygments.lexers.web import XmlLexer
from pygments.formatters.html import HtmlFormatter

#===============
# Custom Widgets
#===============


class PygmentsCodeWidget(forms.Widget):
    """
    Custom Widget to show Pygments-Highlighted fragments of Code.
    """

    def __init__(self, lexer_cls=None, style_attrs=None, attrs=None):

        default_style_attrs = {
            'width': '1024px',
            'margin-left': '7em',
            'padding_left': '30px',
        }

        if style_attrs:
            default_style_attrs.update(style_attrs)

        style_string = ''
        for k, v in default_style_attrs.iteritems():
            style_string += '%s: %s; ' % (k, v)
        default_attrs = {'style': style_string}

        if attrs:
            default_attrs.update(attrs)
        super(PygmentsCodeWidget, self).__init__(attrs=default_attrs)

        if lexer_cls:
            self.lexer = lexer_cls()
        else:
            self.lexer = None

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        else:
            if not isinstance(value, unicode):
                from codecs import encode
                value = encode(value, 'utf-8')

        final_attrs = self.build_attrs(attrs, name=name)
        # Pygments Lexer
        if not self.lexer:
            try:
                self.lexer = guess_lexer(value)
            except ValueError:
                self.lexer = JavaLexer()
        return format_html(u'<div{0}>\r\n{1}</div>', flatatt(final_attrs),
                           mark_safe(highlight(value, self.lexer, HtmlFormatter())))


class NavigablePygmentsCodeWidget(PygmentsCodeWidget):
    """
    Custom Widget to show Pygments-Highlighted fragments of Code.

    This Widget is different from the Superclass in the sense that
    this one shows the target fragment of code into a table along with
    anchors for every code line.
    These anchors corresponds to code line. In this way, the Pygment-Highlighted
    code fragment may be also referencable by line numbers.

    This widget is used to show `SourceCodeFile` instances.
    """

    def render(self, name, value, attrs=None):
        """
        Display the code stream into a referenciable HTML
        table with an hyperlink for each line of the source file.
        """
        if value is None:
            value = ''
        else:
            if not isinstance(value, unicode):
                from codecs import encode
                value = encode(value, 'utf-8')

        final_attrs = self.build_attrs(attrs, name=name)
        # Pygments Lexer
        if not self.lexer:
            try:
                self.lexer = guess_lexer(value)
            except ValueError:
                self.lexer = JavaLexer()

        table_rows = u''
        for i, line in enumerate(value.splitlines(True)):
            emph_line = highlight(line, self.lexer, HtmlFormatter())
            emph_line = emph_line.replace('<div class="highlight">','').replace('</div>', '')
            table_rows += u'<tr class="highlight"><td class="line"><a id="{0}">{0}</a></td>' \
                          u'<td>{1}</td></tr>\r\n'.format(i+1, mark_safe(emph_line))
        return format_html(u'<table{0}><tbody>{1}</tbody></table>', flatatt(final_attrs),
                           mark_safe(table_rows))



#============
# Admin Forms
#============

class SoftwareProjectAdminForm(forms.ModelForm):
    """
    Form for the `SoftwareProject` model class.

    Please note that this form inherits from `django.forms.Form` instead
    from `django.forms.ModelForm` as it is going to be used (only)
    for the (Django) admin site.

    Further information can be found in the *Note* just after the
    `ModelAdmin.form` option:
    [https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#modeladmin-options]
    """

    def clean_src_package_file(self):
        in_mem_uploadfile = self.cleaned_data['src_package_file']
        package_filename = in_mem_uploadfile.name
        filetype, encoding = mimetypes.guess_type(package_filename)

        accepted_encodings = ACCEPTED_MIMETYPES.values()
        accepted_mimetypes = ACCEPTED_MIMETYPES.keys()

        if not filetype and not encoding:
            raise ValidationError(_('The input file is not a valid Compressed Archive'))

        if filetype:
            if not filetype in accepted_mimetypes:
                raise ValidationError(_('The Input file is not a valid Compressed Archive'))
        elif encoding:
            if not encoding in accepted_encodings:
                raise ValidationError(_('The Input file is not a valid Compressed Archive'))

        return self.cleaned_data['src_package_file']


class CodeArtifactAdminForm(forms.ModelForm):
    """
    Custom form class for `CodeArtifact` model instances used in the
    Admin site.
    This form class is used in the `change_view` admin view for both
    `CodeClass` and `CodeMethod` instances.
    """

    class Meta:
        widgets = {
            'code_fragment': PygmentsCodeWidget(),
            'comment': PygmentsCodeWidget(),
            'xml_tree': PygmentsCodeWidget(lexer_cls=XmlLexer),
        }

class CodeArtifactModifyAdminForm(forms.ModelForm):
    """
    Alternate AdminForm to be associated to `CodeMethod` instances
    only in case the current user is an admin (superuser).

    Differently from the previous one (i.e., `CodeArtifactAdminForm`),
    this forms includes default widgets to make the fields changeable.

    For additional information, see the method `get_form` in
    `CodeMethodAdmin`.
    """


class InlineCodeArtifactAdminForm(forms.ModelForm):
    """
    Similarly to the `CodeArtifactAdminForm`, this form class specifies a set of
    `PygmentsCodeWidget` widgets to be used for code-based form fields.
    However, differently from the other form class, this one removes the XML
    field as it is used for `InlineAdminModel` (see `admin.InlineCodeMethodAdmin`)
    """

    class Meta:
        widgets = {
            'code_fragment': PygmentsCodeWidget(),
            'comment': PygmentsCodeWidget(),
        }


class AgreementEvaluationAdminForm(forms.ModelForm):
    """
    This form class is used in the `AgreementEvaluationAdmin` to show
    both `AgreementEvaluation` fields along with some `CodeMethod` fields.

    Please note that `AgreementEvaluation` fields are automatically fed from the
    associated model class.
    """

    method_name = forms.CharField(label=_('Method name'), required=False,
                                  widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    start_line = forms.IntegerField(label=_('Start line'), required=False,
                                    widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    end_line = forms.IntegerField(label=_('End line'), required=False,
                                  widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    code_fragment = forms.CharField(label=_('Method Code'), required=False,
                                    widget=PygmentsCodeWidget(style_attrs={'width': 'auto'}))
    code_comment = forms.CharField(label=_('Method Comment'), required=False,
                                   widget=PygmentsCodeWidget(style_attrs={'width': 'auto'}))

    def __init__(self, *args, **kwargs):
        super(AgreementEvaluationAdminForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']
        if instance:
            self.fields['method_name'].initial = instance.reference_method.method_name
            self.fields['start_line'].initial = instance.reference_method.start_line
            self.fields['end_line'].initial = instance.reference_method.end_line
            self.fields['code_fragment'].initial = instance.reference_method.code_fragment
            self.fields['code_comment'].initial = instance.reference_method.comment

    class Meta:
        model = AgreementEvaluation


class SourceCodeFileAdminForm(forms.ModelForm):
    """
    Model form class for `SourceCodeFile` instances.
    This forms is necessary only to map a custom widget
    (i.e., `NavigablePygmentsCodeWidget`) for the
    `source_code_text` field.
    """

    class Meta:
        widgets = {
            'source_code_text': NavigablePygmentsCodeWidget(),
        }


#==============================
# Admin Changelist Filter Forms
#==============================

class AdminFilterSoftwareProject(forms.Form):
    """
    Admin filter form based on `reference_method.project` field values
    """
    reference_method__project = forms.ChoiceField(label=_('Project'))

    def __init__(self, request, *args, **kwargs):
        super(AdminFilterSoftwareProject, self).__init__(*args, **kwargs)

        self.fields['reference_method__project'].choices = [("", _("----------"))]
        self.fields['reference_method__project'].choices.extend(
            [(project.id, project) for project in SoftwareProject.objects.all()
                if project.has_code_base]
        )

        if request.GET and 'reference_method__project' in request.GET:
            selected_project = request.GET.get('reference_method__project')
            self.fields['reference_method__project'].initial = selected_project


class AdminFilterCodeClass(forms.Form):
    """
    Admin filter form based on `reference_method.code_class` field values
    """
    reference_method__code_class = forms.ChoiceField(label=_('Code Class'))

    def __init__(self, request, *args, **kwargs):
        super(AdminFilterCodeClass, self).__init__(*args, **kwargs)

        self.fields['reference_method__code_class'].choices = [("", _("----------"))]

        # To simplify the usability of CodeClass Filtering, in case a "filter by project"
        # is also applied, Classes shown in the filter are restricted to the ones
        # belonging to the selected project.
        if 'reference_method__project' in request.GET and request.GET['reference_method__project']:
            target_project_id = int(request.GET['reference_method__project'])
            code_classes = CodeClass.objects.filter(project__id=target_project_id)
        else:
            code_classes = CodeClass.objects.all()

        self.fields['reference_method__code_class'].choices.extend(
            [(code_class.id, code_class) for code_class in code_classes
             if code_class.methods.count() > 0]
        )

        if request.GET and 'reference_method__code_class' in request.GET:
            selected_class = request.GET.get('reference_method__code_class')
            self.fields['reference_method__code_class'].initial = selected_class


class AdminFilterEvaluated(forms.Form):
    """
    Admin filter form based on `evaluated` field values
    """
    evaluated = forms.TypedChoiceField(label=_('Evaluated'), coerce=bool)

    def __init__(self, request, *args, **kwargs):
        super(AdminFilterEvaluated, self).__init__(*args, **kwargs)
        self.fields['evaluated'].choices = [('', _('All')), ('0', _('False')),
                                            ('1', _('True'))]

        if request.GET and 'evaluated' in request.GET:
            self.fields['evaluated'].initial = request.GET.get('evaluated')


class AdminFilterEvaluator(forms.Form):
    """
    Admin filter form based on `evaluator` field values.
    This filter is publicly enabled only for superusers.
    """
    evaluator = forms.ChoiceField(label=_('Evaluator'))

    def __init__(self, request, *args, **kwargs):
        super(AdminFilterEvaluator, self).__init__(*args, **kwargs)

        self.fields['evaluator'].choices = [("", _("----------"))]
        self.fields['evaluator'].choices.extend([(user.id, user) for user in
            User.objects.exclude(is_active=False).filter(is_staff=True).exclude(is_superuser=True)])
        if request.GET and 'evaluator' in request.GET:
            self.fields['evaluator'].initial = request.GET.get('evaluator')


class AdminFilterAgreementVote(forms.Form):
    """
    Admin filter form based on `evaluator` field values.
    This filter is publicly enabled only for superusers.
    """
    agreement_vote = forms.ChoiceField(label=_('Agreement Vote'))

    def __init__(self, request, *args, **kwargs):
        super(AdminFilterAgreementVote, self).__init__(*args, **kwargs)

        self.fields['agreement_vote'].choices = [("", _("----------"))]
        self.fields['agreement_vote'].choices.extend(AGREEMENT_RATES[1:-1])
        if request.GET and 'agreement_vote' in request.GET:
            self.fields['agreement_vote'].initial = request.GET.get('agreement_vote')
