"""DataLad demo module"""

__docformat__ = 'restructuredtext'

from os.path import curdir
from os.path import abspath

from datalad.interface.base import Interface
from datalad.interface.base import build_doc
from datalad.support.param import Parameter
from datalad.distribution.dataset import datasetmethod
from datalad.interface.utils import eval_results
from datalad.support.constraints import EnsureChoice

from datalad.interface.results import get_status_dict

module_suite = (
    "Demo DataLad command suite",
    [
        (
            'dmhelloworld',
            'HelloWorld',
            'hello-cmd',
            'hello_py'
        ),
    ]
)


@build_doc
class HelloWorld(Interface):
    """Short description of the command

    Long description of arbitrary volume.
    """

    _params_ = dict(
        language=Parameter(
            args=("-l", "--language"),
            doc="""language to say "hello" in""",
            constraints=EnsureChoice('en', 'de')),
    )

    @staticmethod
    @datasetmethod(name='hello')
    @eval_results
    def __call__(language='en'):
        if language == 'en':
            msg = 'Hello!'
        elif language == 'de':
            msg = 'Tachchen!'
        else:
            msg = ("unknown language: '%s'", language)

        yield get_status_dict(
            action='demo',
            path=abspath(curdir),
            status='ok' if language in ('en', 'de') else 'error',
            message=msg)
