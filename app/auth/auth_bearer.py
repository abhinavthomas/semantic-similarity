import os
import time
from typing import List, Tuple

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()


class JWTBearer(HTTPBearer):
    def __init__(self, applications: List[str] = [], roles: List[str] = [], auto_error: bool = True):
        self.JWT_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
        self.JWT_ALGORITHM = "HS256"
        self.roles = roles
        self.applications = applications
        super(JWTBearer, self).__init__(auto_error=auto_error)

    def decodeJWT(self, token: str) -> dict:
        try:
            decoded_token = jwt.decode(
                token, self.JWT_SECRET, algorithms=[self.JWT_ALGORITHM])
            errorCode = None if decoded_token.get(
                "exp") is not None and decoded_token.get("exp") >= time.time() else 401
            return decoded_token, errorCode
        except jwt.exceptions.ExpiredSignatureError:
            return {}, 401
        except Exception as e:
            return None, 403

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme.")
            isTokenValid, permissions, errorCode = self.verify_jwt(
                credentials.credentials)
            if not isTokenValid:
                raise HTTPException(
                    status_code=403, detail="Invalid token")
            elif errorCode:
                raise HTTPException(
                    status_code=401, detail="Token expired")
            else:
                for app in self.applications:
                    if app not in permissions.get('applications'):
                        raise HTTPException(
                            status_code=403, detail="Not authorization: No access to application")
                for role in self.roles:
                    if role not in permissions.get('roles'):
                        raise HTTPException(
                            status_code=403, detail="Not authorization: Role not present")
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> Tuple[bool, List[str], int]:
        isTokenValid: bool = False
        permissions = None
        payload, errorCode = self.decodeJWT(jwtoken)
        isTokenValid = payload is not None
        if isTokenValid:
            permissions = payload.get('permissions')
        return isTokenValid, permissions, errorCode
