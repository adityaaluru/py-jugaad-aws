## HTTP Exceptions

#For status code 400
class BadRequestError(Exception):
    pass
#For status code 401
class UnAuthorizedError(Exception):
    pass
#For status code 403
class ForbiddenError(Exception):
    pass
#For status code 404
class NotFoundError(Exception):
    pass
#For status code 413
class LargeResponseError(Exception):
    pass
#For status code 500
class InternalServerError(Exception):
    pass