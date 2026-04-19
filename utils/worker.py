from PyQt6.QtCore import QThread, pyqtSignal


class AnalysisWorker(QThread):
    """Generic worker thread for any analysis agent."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, agent_cls, *args, **kwargs):
        super().__init__()
        self._agent_cls = agent_cls
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            agent = self._agent_cls()
            result = agent.analyze(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
