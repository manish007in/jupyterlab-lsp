import os
import pathlib
import shutil
import sys
from typing import Callable, Dict, List, Text

from jupyterlab.commands import get_app_dir
from notebook.transutils import _
from traitlets import List as List_, Unicode, default
from traitlets.config import LoggingConfigurable

# TODO: TypedDict?
LanguageServerSpec = Dict[Text, List[Text]]
KeyedLanguageServerSpecs = Dict[Text, LanguageServerSpec]


class LanguageServerManagerAPI(LoggingConfigurable):
    """ Public API that can be used for python-based connectors
    """

    nodejs = Unicode(help=_("path to nodejs executable")).tag(config=True)

    node_roots = List_([], help=_("absolute paths in which to seek node_modules")).tag(
        config=True
    )

    extra_node_roots = List_(
        [], help=_("additional absolute paths to seek node_modules first")
    ).tag(config=True)

    def find_node_module(self, *path_frag):
        """ look through the node_module roots to find the given node module
        """
        for candidate_root in self.extra_node_roots + self.node_roots:
            candidate = pathlib.Path(candidate_root, "node_modules", *path_frag)
            if candidate.exists():
                return str(candidate)

    @default("nodejs")
    def _default_nodejs(self):
        return (
            shutil.which("node") or shutil.which("nodejs") or shutil.which("nodejs.exe")
        )

    @default("node_roots")
    def _default_node_roots(self):
        """ get the "usual suspects" for where node_modules may be found

        - where this was launch (usually the same as NotebookApp.notebook_dir)
        - the JupyterLab staging folder
        - wherever conda puts it
        - wherever some other conventions put it
        """
        return [
            os.getcwd(),
            pathlib.Path(get_app_dir()) / "staging",
            pathlib.Path(sys.prefix) / "lib",
            # TODO: "well-known" windows paths
            sys.prefix,
        ]


# Gotta be down here so it can by typed... really should have a IL
SpecMaker = Callable[[LanguageServerManagerAPI], KeyedLanguageServerSpecs]
