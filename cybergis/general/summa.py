import logging
import os
from .keeling import KeelingJob, KeelingSBatchScript
from .base import AbstractScript
from string import Template

logger = logging.getLogger("cybergis")



class SummaKeelingSBatchScript(KeelingSBatchScript):

    simg_remote_path = None
    userscript_remote_path = None
    EXEC = "singularity exec $simg $userscript"

    def __init__(self, walltime, node, jobname, userscript_path, *args, **kargs):
        userscript_path=userscript_path+"/run.py"
        _exec = Template(self.EXEC).substitute(simg="/data/keeling/a/zhiyul/images/pysumma_ensemble.img", userscript=userscript_path)
        super().__init__(walltime, node, jobname, _exec, *args, **kargs)


class SummaUserScript(AbstractScript):

    SUMMA_USER_TEMPLATE = '''
import pysumma as ps
import pysumma.hydroshare_utils as utils
from hs_restclient import HydroShare
import shutil, os
import subprocess
from ipyleaflet import Map, GeoJSON
import json

os.chdir("$local_path")
instance = '$instance_name'

file_manager = os.getcwd() + '/' + instance + '/settings/$file_manager_name'
executable = "/code/bin/summa.exe"

S = ps.Simulation(executable, file_manager)


S.run('local', run_suffix='_test')

'''

    local_path = None
    instance_name = None
    file_manager_name = None
    userscript_name = "run.py"

    def __init__(self, local_path, instance_name, file_manager_name, *args, **kargs):
        self.local_path=local_path
        self.instance_name=instance_name
        self.file_manager_name=file_manager_name

    def generate_script(self, local_folder_path=None, *args, **kargs):

        uscript = Template(self.SUMMA_USER_TEMPLATE).substitute(
                local_path=self.local_path,
                instance_name=self.instance_name,
                file_manager_name=self.file_manager_name
                )
        logger.debug(uscript)
        if not os.path.exists(local_folder_path) or not os.path.isdir(local_folder_path):
            return uscript
        else:
            local_path = os.path.join(local_folder_path, self.userscript_name)
            with open(local_path, "w") as f:
                f.write(uscript)
            logging.debug("SummaUserScript saved to {}".format(local_path))


class SummaKeelingJob(KeelingJob):

    JOB_ID_PREFIX = "Summa_"
    sbatch_script_class = SummaKeelingSBatchScript
    user_script_class = SummaUserScript

    def __init__(self, local_workspace_path, connection, sbatch_script, user_script, local_id=None, *args, **kwargs):

        if local_id is None:
            local_id = self.random_id(prefix=self.JOB_ID_PREFIX)

        super().__init__(local_workspace_path, connection, sbatch_script, user_script, local_id=local_id, *args, **kwargs)
