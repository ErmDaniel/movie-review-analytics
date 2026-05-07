from enum import IntEnum

class ReviewStatus(IntEnum):
    PUBLISHED = 1
    HIDDEN = 2
    DELETED = 3

class UserRole(IntEnum):
    USER = 1
    ADMIN = 2
    MODERATOR = 3