class ProjectError(Exception):
    pass

class Validation_Error(ProjectError):
    pass

class PasswordError(ProjectError):
    pass