import logging
import os
from .base import *
from .connection import *
from .keeling import *
from .summa import *
from .utils import *
from .job import *
from .summaUI import *
import time
from ipywidgets import *
from IPython.display import display

logger = logging.getLogger("cybergis")
logger.setLevel("DEBUG")
streamHandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

def Labeled(label, widget):
    width='130px'
    return (Box([HTML(value='<p align="right" style="width:%s">%s&nbsp&nbsp</p>'%(width,label)),widget],
                layout=Layout(display='flex',align_items='center',flex_flow='row')))


def Title():
    return (Box([HTML(value='<h1>Welcome to Summa General Case</h1>')],
        layout=Layout(display='flex',align_items='center',flex_flow='row')
        ))

class summaUI():
    username = ""
    machine = ""
    model_source_folder_path = "/Users/CarnivalBug/general_summa/Jupyter-xsede/SummaModel_ReynoldsAspenStand_StomatalResistance_sopron" ## the path to the summa testcase folder
    file_manager_path = "/Users/CarnivalBug/general_summa/Jupyter-xsede/SummaModel_ReynoldsAspenStand_StomatalResistance_sopron/settings/summa_fileManager_riparianAspenSimpleResistance.txt" ## the path to the filemanager folder
    jobname = "test" ## the name of the job
    walltime = 10
    node = 1
    keeling_con = None
    nNodes=IntSlider(
        value=5,
        min=1,
        max=10,
        step=1,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d',
        slider_color='white'
    )
    walltime=FloatSlider(
        value=10,
        min=1.0,
        max=48.0,
        step=1.0,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.1f',
        slider_color='white'
    )
    confirm=Button(
        description='Submit Job',
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Submit job'
    )


    def __init__(self, username="gisolve", machine="keeling"):
        self.username=username
        self.machine="keeling"

    def submit(self, b):
        self.node = self.nNodes.value
        self.walltime = self.walltime.value
        model_source_folder_path = self.model_source_folder_path
        file_manager_path = self.file_manager_path
        summa_sbatch = SummaKeelingSBatchScript(self.walltime, self.node, self.jobname)
        sjob = SummaKeelingJob("/tmp", self.keeling_con, summa_sbatch, model_source_folder_path, file_manager_path, name=self.jobname)
        sjob.prepare()
        for i in range(100):
            time.sleep(1)
            print(sjob.job_status())

        a = 1

    def runSumma(self):
        if (self.machine=="keeling"):
            if (self.username == "gisolve"):
                self.keeling_con = SSHConnection("keeling.earth.illinois.edu",
                            user_name="cigi-gisolve",
                            key_path="/Users/CarnivalBug/Desktop/gisolve.key")
            else:
                self.keeling_con = SSHConnection("keeling.earth.illinois.edu",
                            user_name="flu8")
                self.keeling_con.login()
        else:
            print ("Not implemented yet")

        self.__submitUI()


    def __submitUI(self):
        submitForm=VBox([
            Title(),
            Labeled('Walltime (h)', self.walltime),
            Labeled('Nodes', self.nNodes),
            Labeled('', self.confirm)
        ])
        display(submitForm)
        self.confirm.on_click(self.submit)



