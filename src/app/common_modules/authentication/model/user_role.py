from enum import IntEnum


class UserRole(IntEnum):
    USER = 1
    ADMIN = 2
    SYSTEM_ADMIN = 3

    @property
    def display_name(self):
        return {
            UserRole.USER: "User",
            UserRole.ADMIN: "Administrator",
            UserRole.SYSTEM_ADMIN: "System Administrator"
        }[self]

    @property
    def prefixed_display_name(self):
        return {
            UserRole.USER: "a User",
            UserRole.ADMIN: "an Administrator",
            UserRole.SYSTEM_ADMIN: "a System Administrator"
        }[self]
