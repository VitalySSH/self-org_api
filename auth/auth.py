from auth.implementations import AuthService
from auth.token.delivery.cookie import CookieTokenDelivery
from auth.token.jwt_token import JWTTokenService

token_service = JWTTokenService()
token_delivery = CookieTokenDelivery()
auth_service = AuthService(
    token_service=token_service, token_delivery=token_delivery)