from auth.services.auth_service import AuthUserService
from auth.token.delivery.cookie import CookieTokenDelivery
from auth.token.jwt_token import JWTTokenService

token_service = JWTTokenService()
token_delivery = CookieTokenDelivery()
auth_service = AuthUserService(
    token_service=token_service,
    token_delivery=token_delivery,
)
