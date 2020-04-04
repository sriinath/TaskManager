class TaskManagerError(Exception):
    def __init__(self, message, status='Failure', status_code=500):
        self.status = status
        self.message = message
        self.status_code = status_code