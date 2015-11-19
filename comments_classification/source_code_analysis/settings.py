"""
:Author: Valerio Maggio
:Organization: University of Naples Federico II
:Contact: valerio.maggio@unina.it

"""

from django.utils.translation import gettext_lazy as _

ACCEPTED_MIMETYPES = {
    'application/x-bzip': 'bzip2',
    'application/x-tar': 'gzip',
    'application/zip': 'zip',
    }


# The list of Programming Language Analysis supported
LANGUAGES = (
    # (code file extension, lang name)
    ('.java', 'Java'),
)
DEFAULT_LANG = '.java'

#=========================
# Agreement Rates Settings
#=========================

STRONG_DISAGREEMENT = _("Strong Disagreement")

STRONG_AGREEMENT = _("Strong Agreement")

AGREEMENT = _("Agreement")

DONT_KNOW = _("Don't Know")

DISAGREEMENT = _("Disagreement")

FURTHER_EVAL = _("To Be Checked")

DEFAULT_AGREEMENT = -1
DEFAULT_AGREEMENT_LABEL = '----------'

AGREEMENT_RATES = (
    (DEFAULT_AGREEMENT, DEFAULT_AGREEMENT_LABEL),
    (0, STRONG_DISAGREEMENT),
    (1, DISAGREEMENT,),
    (2, DONT_KNOW,),
    (3, AGREEMENT,),
    (4, STRONG_AGREEMENT,),
    (5, FURTHER_EVAL,),
)

AGREEMENT_RATES_NO_TRANS = (
    (DEFAULT_AGREEMENT, DEFAULT_AGREEMENT_LABEL),
    (0, "Strong Disagreement"),
    (1, "Disagreement",),
    (2, "Don't Know",),
    (3, "Agreement",),
    (4, "Strong Agreement",),
    (5, "To Be Checked",),
)

#========================
# Code Analysis Settings
#========================

FILES_PER_TASK = 10
