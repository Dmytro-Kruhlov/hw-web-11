from typing import List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, Role
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and takes in any arguments that are required to do so.
        In this case, we're taking in a list of allowed roles.

        :param self: Represent the instance of the class
        :param allowed_roles: List[Role]: Define the allowed roles for a user
        :return: None
        :doc-author: Trelent
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_current_user)):
        """
        The __call__ function is the function that will be called when a user tries to access this endpoint. It takes
        in two arguments: request and current_user. The request argument is an object containing information about
        the HTTP Request, such as its method (GET, POST, etc.) and URL. The current_user argument is an object
        containing information about the currently logged-in user (if there is one). This value comes from our
        auth_service dependency.

        :param self: Access the class attributes
        :param request: Request: Get the request object
        :param current_user: User: Pass the user object from the auth_service
        :return: A function that takes a request and current_user as parameters
        :doc-author: Trelent
        """
        print(request.method, request.url)
        print(f"User role {current_user.role}")
        print(f"Allowed roles: {self.allowed_roles}")
        if current_user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden")

