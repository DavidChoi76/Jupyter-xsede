import logging
import os
from string import Template

logger = logging.getLogger("cybergis")


class BaseConnection(object):
    connection_type = str()
    server = str()

    def login(self):
        raise NotImplementedError()

    def logout(self):
        raise NotImplementedError()

    def upload(self, local_fpath, remote_fpath, *args, **kwargs):
        raise NotImplementedError()

    def download(self, remote_fpath, local_fpath, *args, **kwargs):
        raise NotImplementedError()

    def run_command(self, command, *args, **kwargs):
        raise NotImplementedError()


class BaseScript(object):
    name = "BaseScript"
    file_name = "script.sh"
    _local_path = ""
    SCRIPT_TEMPLATE = str()

    @property
    def local_path(self):
        return self._local_path

    def parameter_dict(self, *args, **kwargs):
        raise NotImplementedError()

        return dict()

    def generate_script_old(self, local_folder_path=None):
        script = Template(self.SCRIPT_TEMPLATE).substitute(
            **self.parameter_dict()
        )
        logger.debug(script)
        if os.path.isdir(local_folder_path):
            self.local_path = os.path.join(local_folder_path, self.file_name)
            with open(self.local_path, 'w') as f:
                f.write(script)
            logger.debug("{} saved to {}".format(self.name, self.local_path))
            return self.local_path
        else:
            return script

    def generate_script(self, local_folder_path=None, parameter_dict=None):
        local_folder_path = str(local_folder_path)
        if not isinstance(parameter_dict, dict):
            parameter_dict = self.parameter_dict()

        for k, v in parameter_dict.items():
            if isinstance(v, BaseScript):
                script_path = v.generate_script(local_folder_path)
                parameter_dict[k] = script_path

        script = Template(self.SCRIPT_TEMPLATE).substitute(
            **parameter_dict
        )
        logger.debug(script)
        if os.path.isdir(local_folder_path):
            self._local_path = os.path.join(local_folder_path, self.file_name)
            with open(self.local_path, 'w') as f:
                f.write(script)
            logger.debug("{} saved to {}".format(self.name, self.local_path))
            return self.local_path
        else:
            return script


class BaseJob(object):
    pass


class SBatchScript(BaseScript):
    name = "SBatchScript"
    file_name = "sbatch.sh"
    SCRIPT_TEMPLATE = '''
    #!/bin/bash
    #SBATCH --job-name=$jobname
    #SBATCH --nodes=$nodes
    #SBATCH -t $walltime

    $exec'''

    walltime = int(100)
    nodes = int(1)
    jobname = ""
    stdout = None  # Path to output
    stderr = None  # Path to err
    exec = ""

    def __init__(self, walltime, nodes, jobname, exec, stdout=None, stderr=None, file_name=None):
        self.walltime = walltime
        self.nodes = nodes
        self.jobname = jobname
        self.exec = exec
        self.stdout = stdout
        self.stderr = stderr
        self.file_name = file_name

    def parameter_dict(self, *args, **kwargs):
        return dict(walltime=self.walltime,
                    jobname=self.jobname,
                    nodes=self.nodes,
                    exec=self.exec)




