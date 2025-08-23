class IncorrectConfigException(Exception):
    pass


class WrongGuildException(Exception):
    pass


class WrongUserException(Exception):
    pass

class UserNotMemberException(Exception):
    pass

class InvalidTicketIdException(Exception):
    pass

class TicketHolderRoleAlreadyAssignedException(Exception):
    pass

class TicketAlreadyClaimedException(Exception):
    pass

class MemberHasNotReactedToCocException(Exception):
    pass

class TicketNotFoundInDatabaseException(Exception):
    pass

class RoleAssignmentFailedException(Exception):
    pass

class EmptyRoleException(Exception):
    pass