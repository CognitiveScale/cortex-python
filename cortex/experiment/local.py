"""
Copyright 2023 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import List
import os

from pathlib import Path
from contextlib import closing
from datetime import datetime
import dill

from .model import Run, _to_html
from ..exceptions import ConfigurationException
from ..properties import PropertyManager

from ..utils import get_logger

log = get_logger(__name__)


class LocalExperiment:
    """
    Runs experiment locally, not using Cortex services.
    """

    config_file = "config.yml"
    root_key = "experiment"
    dir_cortex = ".cortex"
    dir_local = "local"
    dir_artifacts = "artifacts"
    dir_experiments = "experiments"
    runs_key = "runs"

    def __init__(self, name, basedir=None):
        self._name = name

        if basedir:
            self._basedir = Path(basedir)
        else:
            self._basedir = Path.home() / self.dir_cortex

        self._work_dir = (
            self._basedir / self.dir_local / self.dir_experiments / self.name
        )
        self._work_dir.mkdir(parents=True, exist_ok=True)
        Path(self._work_dir / self.dir_artifacts).mkdir(parents=True, exist_ok=True)

        # Initialize config
        prop_mgr = PropertyManager()
        try:
            prop_mgr.load(str(self._work_dir / self.config_file))
        except FileNotFoundError:
            prop_mgr.set("meta", {"created": str(datetime.now())})

        self._config = prop_mgr

    @property
    def name(self) -> str:
        """Name of the experiment.

        :return: Name of the experiment.
        :rtype: str
        """
        return self._name

    def start_run(self) -> Run:
        """Creates a run for the experiment.
        :rtype: :class:`cortex.experiment.model.Run`
        """
        return Run(self)

    def save_run(self, run: Run) -> None:
        """Saves a run.

        :param run: The run you want to save.
        :type run: :class:`cortex.experiment.model.Run`

        :rtype: None
        """
        updated_runs = []
        runs = self._config.get(self._config.join(self.root_key, self.runs_key)) or []
        replaced = False
        if len(runs) > 0:
            for each_run in runs:
                if each_run["id"] == run.id:
                    updated_runs.append(run.to_json())
                    replaced = True
                else:
                    updated_runs.append(each_run)

        if not replaced:
            updated_runs.append(run.to_json())

        self._config.set(self._config.join(self.root_key, self.runs_key), updated_runs)
        self._save_config()

        for name, artifact in run.artifacts.items():
            with closing(open(self.get_artifact_path(run, name), "wb")) as file_d:
                dill.dump(artifact, file_d)

    def reset(self):
        """
        Resets the experiment, removing all associated configuration and runs.
        """
        self._config.remove_all()
        self.clean_dir(self._work_dir)
        self.clean_dir(Path(self._work_dir / self.dir_artifacts))

    def clean_dir(self, dir_to_clean: str) -> None:
        """Removes only the files from the given directory

        :param dir_to_clean: Directory to remove files from
        :type dir_to_clean: str
        :rtype: None
        """
        for file_d in os.listdir(dir_to_clean):
            if os.path.isfile(os.path.join(dir_to_clean, file_d)):
                os.remove(os.path.join(dir_to_clean, file_d))

    def set_meta(self, prop: str, value: any) -> None:
        """Associates metadata properties with the experiment.

        :param prop: The name of the metadata property to associate with the experiment.
        :type prop: str
        :param value: The value of the metadata property to associate with the experiment. Needs to be serializable to JSON
        :type value: any
        """  # pylint: disable=line-too-long
        meta = self._config.get("meta")
        meta[prop] = value
        self._config.set("meta", meta)
        self._save_config()

    def runs(self) -> List[Run]:
        """Returns the runs associated with the experiment.
        :rtype: List[Run]
        """
        props = self._config
        runs = props.get(props.join(self.root_key, self.runs_key)) or []
        return [Run.from_json(r, self) for r in runs]

    def get_run(self, run_id: str) -> Run:
        """Gets a particular run from the runs in this experiment.

        :param run_id: Identifier of the run to be fetched
        :type run_id: str
        :rtype: :class:`cortex.experiment.model.Run`
        """
        for run in self.runs():
            if run.id == run_id:
                return run
        return None

    def last_run(self) -> Run:
        """Returns the most recent run of this experiment

        :return: _description_
        :rtype: Run
        """
        runs = self.runs()
        if len(runs) > 0:
            return runs[-1]
        return None

    def find_runs(self, filter_obj, sort, limit: int) -> List[Run]:
        """find_runs is not supported in local mode

        :raises NotImplementedError: _description_
        :rtype: List[Run]
        """
        raise NotImplementedError("find_runs is not supported in local mode")

    def _save_config(self):
        self._config.save(self._work_dir / self.config_file)

    def load_artifact(self, run: Run, name: str, extension: str = "pk") -> any:
        """Returns a particular artifact created by the given run of the experiment.

        :param run: The run that generated the artifact requested.
        :type run: Run
        :param name: The name of the artifact.
        :type name: str
        :param extension: An optional extension, defaults to "pk"
        :type extension: str, optional
        :return: Python objects loaded into memory from the artifact content
        :rtype: Any
        """
        artifact_file = self.get_artifact_path(run, name, extension)
        with closing(open(artifact_file, "rb")) as file_d:
            return dill.load(file_d)

    def get_artifact_path(self, run: Run, name: str, extension: str = "pk") -> str:
        """Returns the fully qualified path to a particular artifact.

        :param run: The run that generated the artifact requested.
        :type run: Run
        :param name:  The name of the artifact.
        :type name: str
        :param extension: An optional extension, defaults to "pk"
        :type extension: str, optional
        :return: A local filesystem path to the artifact
        :rtype: str
        """
        return (
            self._work_dir
            / self.dir_artifacts
            / "{}_{}.{}".format(name, run.id, extension)
        )

    def _repr_html_(self):
        return _to_html(self)

    def display(self):
        # pylint: disable=import-outside-toplevel
        """
        Provides html output of the experiment. Useful in Jupyter notebooks
        """
        try:
            from IPython.display import (
                display,
                HTML,
            )

            display(HTML(self._repr_html_()))
        except ImportError as exc:
            raise ConfigurationException(
                "The ipython package is required, please install it"
                "using pip install cortex-python[viz]"
            ) from exc
