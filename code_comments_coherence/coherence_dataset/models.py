from django.db import models

from source_code_analysis.models import CodeMethod
from .settings import COHERENCE_CHOICES

class Example(models.Model):
    method = models.OneToOneField(CodeMethod, related_name='example')
    target = models.IntegerField(choices=COHERENCE_CHOICES)

    @property
    def code(self):
        return self.method.lexical_info.normalized_code

    @property
    def comment(self):
        return self.method.lexical_info.normalized_comment
