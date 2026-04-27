class ProjectError(Exception):
    pass

class Validation_Error(ProjectError):
    pass

class PasswordError(ProjectError):
    pass

class ServiceError(ProjectError):
    pass

class ServiceTypeError(ServiceError):
    pass

class ServiceIndexError(ServiceError):
    pass

class ServiceValidationError(ServiceError):
    pass