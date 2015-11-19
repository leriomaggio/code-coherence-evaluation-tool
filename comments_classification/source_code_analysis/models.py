from django.db import models
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .settings import LANGUAGES, DEFAULT_LANG, AGREEMENT_RATES, DEFAULT_AGREEMENT

# Highlight
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers.compiled import JavaLexer
from pygments.formatters.html import HtmlFormatter

from django.utils.html import clean_html


def src_package_upload(instance, filename):
    folder_name = os.path.join(instance.name.lower().replace(' ', '_'),
                               instance.version.replace(' ', ''),
                               filename.lower().replace('.', ''))
    return os.path.join(folder_name, filename)


class SoftwareProject(models.Model):
    """
    Model class for a Software Project
    """

    name = models.CharField(max_length=100, verbose_name=_('Project Name'))

    version = models.CharField(max_length=10, verbose_name=_('Project Version'))

    project_url = models.URLField(verbose_name=_('Project URL'))

    src_folder_path = models.FilePathField(max_length=200, blank=True, null=True,
                                           verbose_name=_("Source Folder Path"),
                                           help_text=_("Path on server where source code files "
                                                       "have been extracted."))

    src_package_file = models.FileField(upload_to=src_package_upload,
                                        verbose_name="Source Code Archive File")

    file_extensions = models.CharField(max_length=20, choices=LANGUAGES, default=DEFAULT_LANG,
                                       help_text=_("The main programming language of the Software "
                                                   "system. <br> Please note that so far, only "
                                                   "the <b>Java</b> language analysis is "
                                                   "supported."),
                                       verbose_name=_('Programming Language'))

    @property
    def source_folder_path(self):
        """
        Returns the Absolute Path for the `src_folder_path` field,
        i.e., MEDIA_ROOT + `src_folder_path`
        """
        return os.path.join(settings.MEDIA_ROOT, self.src_folder_path)

    # ===============================
    # Source Package handling methods
    # (instance methods)
    # ===============================
    def generate_uncompressed_src_archive_path(self):
        upload_folder_name = os.path.dirname(
            src_package_upload(self, os.path.basename(self.src_package_file.path)))
        return os.path.join(settings.MEDIA_ROOT, upload_folder_name, 'extracted')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        TODO: Describe the customization
        """

        # First of all, save the model as it is
        super(SoftwareProject, self).save(force_insert, force_update, using, update_fields)

        # If the `src_folder_path` field is not set, set it uncompressing the archive
        # into the MEDIA_ROOT folder
        uncompressed_fold_pth = self.generate_uncompressed_src_archive_path()
        if not self.src_folder_path or not os.path.exists(uncompressed_fold_pth):
            from setuptools.archive_util import unpack_archive, UnrecognizedFormat
            try:
                unpack_archive(self.src_package_file.path, uncompressed_fold_pth)
                # Set *relative* src_folder_path - remove MEDIA_ROOT to make it machine independent.
                src_folder_path = uncompressed_fold_pth.replace(settings.MEDIA_ROOT, '')
                if src_folder_path.startswith(os.path.sep):
                    src_folder_path = src_folder_path[1:]
                self.src_folder_path = src_folder_path
            except UnrecognizedFormat:
                pass
            else:
                # call the save method again to update the `src_folder_path`
                super(SoftwareProject, self).save(update_fields=['src_folder_path'])

    @property
    def has_code_base(self):
        return (self.code_methods.count() + self.code_classes.count()) > 0

    def __str__(self):
        return '%s (%s)' % (self.name, self.version)

    class Meta:
        verbose_name = _('Software Project')
        verbose_name_plural = _('Software Projects')
        ordering = ['name', 'version']


class SourceCodeFile(models.Model):
    project = models.ForeignKey(SoftwareProject, related_name='source_files')

    filepath = models.FilePathField(max_length=400, verbose_name=_("Source file Path"),
                                    help_text=_("Path on server where source code file "
                                                "has been saved."))

    source_code_text = models.TextField(verbose_name=_('Source Code Text'))

    def __unicode__(self):
        return u'%s@%s' % (os.path.basename(self.filepath), self.project)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if settings.MEDIA_ROOT in self.filepath:
            self.filepath = self.filepath.replace(settings.MEDIA_ROOT, '')
        return super(SourceCodeFile, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _('Source Code File')
        verbose_name_plural = _('Source Code Files')


class CodeArtifact(models.Model):
    """
    ABC for Code Artifacts, i.e., CodeClass and CodeMethod
    """
    file_path = models.CharField(max_length=300, verbose_name=_('Filepath'))
    start_line = models.IntegerField(verbose_name=_('Start line'))
    end_line = models.IntegerField(verbose_name=_('End Line'))

    code_fragment = models.TextField(verbose_name=_('Code Fragment'))
    comment = models.TextField(verbose_name=_('Code Comment'))

    xml_tree = models.TextField(verbose_name=_('AST'))

    @property
    def source_code_fragment(self):
        try:
            lexer = guess_lexer_for_filename(self.file_path, self.code_fragment)
        except ValueError:
            lexer = JavaLexer()
        return highlight(self.code_fragment, lexer, HtmlFormatter())

    @property
    def source_code_comment(self):
        try:
            lexer = guess_lexer_for_filename(self.file_path, self.comment)
        except ValueError:
            lexer = JavaLexer()

        return highlight(self.format_comment(self.comment), lexer, HtmlFormatter())

    @staticmethod
    def format(text_fragment):
        # Reduces four spaces to two spaces (to compress visualization)
        four_space = ' ' * 4
        double_space = ' ' * 2
        text_fragment = text_fragment.replace('\t', four_space).replace(four_space, double_space)
        # Remove useless carriage return
        text_fragment = text_fragment.replace('\n\n', '\n')
        return text_fragment

    def format_comment(self, comment_fragment):
        comment_fragment = self.format(comment_fragment)
        comment_fragment = comment_fragment.replace('/*', '').replace('* ', ' ').replace('*/', '')
        comment_fragment = comment_fragment.replace('*\n', '\n')
        comment_fragment = comment_fragment.replace('&lt;', '<').replace('&gt;', '>')
        return clean_html(comment_fragment)

    def _retrieve_code_fragment(self):
        line_no = 0
        text_fragment = ''
        record = False
        src_filepath = os.path.join(settings.MEDIA_ROOT, self.file_path)
        with open(src_filepath) as src_file:
            for line in src_file:
                line_no += 1
                if line_no == self.start_line:
                    record = True
                elif line_no > self.end_line:
                    break
                if record:
                    text_fragment += line
        self.code_fragment = self.format(text_fragment)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Retrieve the code fragment
        if not self.code_fragment:
            self._retrieve_code_fragment()

        if self.comment:  # format the comment
            self.comment = self.format(self.comment)

        super(CodeArtifact, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        abstract = True
        ordering = ['file_path', 'start_line']


class CodeClass(CodeArtifact):
    """
    Model class for a Code Class
    """
    class_name = models.CharField(max_length=150, verbose_name=_('Class Name'))

    #Reference Information
    project = models.ForeignKey(SoftwareProject, related_name='code_classes',
                                verbose_name=_('Project'))

    @property
    def src_filename(self):
        return os.path.basename(self.file_path)

    @property
    def display_name(self):
        return self.class_name

    def __str__(self):
        return '%s@%s' % (self.class_name, self.src_filename)

    class Meta(CodeArtifact.Meta):
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')


class CodeMethod(CodeArtifact):
    """
    Model class for a Method
    """
    method_name = models.CharField(max_length=150, verbose_name=_('Method Name'))

    # Reference Information
    project = models.ForeignKey(SoftwareProject, related_name='code_methods',
                                verbose_name=_('Project'))
    code_class = models.ForeignKey(CodeClass, related_name='methods', verbose_name=_('Class'))

    @property
    def display_name(self):
        return self.method_name

    def __str__(self):
        return '%s.%s' % (self.code_class.class_name, self.method_name)

    class Meta(CodeArtifact.Meta):
        verbose_name = _('Method')
        verbose_name_plural = _('Methods')
        ordering = ('method_name', 'start_line')


class CodeLexiconInfo(models.Model):
    """
    This model class associates to each Code Method a set of information related
    to its code lexicon.
    So far the model class includes a fields reporting information about:

    - the set of non-english words corresponding to identifiers extracted from source code
    - the set of non-english words corresponding to identifiers extracted from comments
    - the set of `normalized` lexemes (tokens) appearing in the comment
    - the set of `normalized` lexemes (tokens) appearing in the source code
    - the *overlap* value, corresponding to the Jaccard Coefficient between the set of terms
        in code and comments.
    """
    reference_method = models.OneToOneField(CodeMethod, related_name='lexical_info')

    non_eng_tokens_comments = models.TextField(verbose_name=_(u'Non-English Lexemes in Comments'),
                                               blank=True, help_text=_(u'The Set of Non-English'
                                                                       u'Tokens appearing in the '
                                                                       u'Code Method Comment.'))

    non_eng_tokens_code = models.TextField(verbose_name=_(u'Non-English Lexemes in Source Code'),
                                           blank=True, help_text=_(u'The Set of Non-English Tokens'
                                                                   u'appearing in the Code Method'
                                                                   u'Source Code.'))

    normalized_comment = models.TextField(verbose_name=_(u'Normalized Lexemes in Comments'))

    normalized_code = models.TextField(verbose_name=_(u'Normalized Lexemes in Source Code'))

    jaccard_coeff = models.FloatField(verbose_name=_(u'Jaccard Coefficient for Code and Comment'),
                                      default=0.0)

    class Meta:
        verbose_name = _(u'Code Lexicon Information')
        verbose_name_plural = _(u'Code Lexicon Information')


class AgreementEvaluation(models.Model):
    evaluator = models.ForeignKey(User, related_name='evaluations', verbose_name=_('Evaluator'))

    agreement_vote = models.SmallIntegerField(choices=AGREEMENT_RATES, default=DEFAULT_AGREEMENT,
                                              verbose_name=_("Agreement"))

    wrong_association = models.BooleanField(default=False, verbose_name=_('Error in Association'))

    evaluated = models.BooleanField(default=False, editable=False, verbose_name=_('Evaluated'))

    reference_method = models.ForeignKey(CodeMethod, related_name='agreement_evaluations')

    created_datetime = models.DateTimeField(editable=False, auto_now_add=True,
                                            verbose_name=_('Evaluation Created on'))

    last_update = models.DateTimeField(editable=False, auto_now=True, verbose_name=_('Last Update'))

    evaluation_datetime = models.DateTimeField(editable=False, null=True,
                                               verbose_name=_('Evaluated on'))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if self.id and not self.evaluated:
            self.evaluated = True
            if update_fields:  # Check whether the save method call contains `update_fields`
                update_fields.append('evaluated')

        if self.evaluated:
            if self.agreement_vote == DEFAULT_AGREEMENT and not self.wrong_association:
                self.evaluated = False
                self.evaluation_datetime = None
                if update_fields:  # Check whether the save method call contains `update_fields`
                    update_fields.extend(['evaluated', 'evaluation_datetime'])

        super(AgreementEvaluation, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return str(self.reference_method)

    class Meta:
        verbose_name = _('Evaluation')
        verbose_name_plural = _('Evaluations')
        ordering = ['reference_method__code_class__class_name', 'reference_method__start_line']
        app_label = 'agreement_evaluations'


class AgreementEvaluationToBeChecked(AgreementEvaluation):
    """
    Fake Class to allow multiple ModelAdmin Registration
    """
    class Meta:
        proxy = True
        verbose_name = _('Evaluation to be Checked')
        verbose_name_plural = _('Evaluations to be Checked')
        ordering = ['reference_method__code_class__class_name', 'reference_method__start_line']
        app_label = 'agreement_evaluations'