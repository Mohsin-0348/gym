import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class TokenManager:

    @staticmethod
    def get_token(exp, payload, token_type="access"):
        exp = timezone.now().timestamp() + (exp * 60)
        return jwt.encode(
            {
                "exp": exp,
                "type": token_type,
                **payload
            }, settings.SECRET_KEY, algorithm="HS256"
        )

    @staticmethod
    def decode_token(token):
        try:
            decoded = jwt.decode(token, key=settings.SECRET_KEY, algorithms="HS256")
        except jwt.DecodeError:
            return None

        if timezone.now().timestamp() > decoded['exp']:
            return None
        return decoded

    @staticmethod
    def decode_client_token(token):
        try:
            decoded = jwt.decode(token, key=settings.CLIENT_KEY, algorithms="HS256")
        except jwt.DecodeError:
            return None

        return decoded

    @staticmethod
    def get_access(payload):
        token_expiration_time = 24 * 60
        return TokenManager.get_token(token_expiration_time, payload)

    @staticmethod
    def get_refresh(payload):
        token_expiration_time = 24 * 60
        token_type = "refresh"
        return TokenManager.get_token(token_expiration_time, payload, token_type)

    @staticmethod
    def get_email(id_token):
        decoded = jwt.decode(id_token, '', verify=False)
        return decoded.get('email')


class Authentication:

    def __init__(self, request):
        self.request = request

    def authenticate(self):
        data = self.validate_request()

        if not data:
            return None

        return self.get_user(data['user_id'])

    def validate_request(self):
        authorization = self.request.headers.get("AUTHORIZATION", None)
        if not authorization:
            return None

        token = authorization[4:]
        decoded_data = TokenManager.decode_token(token)
        if not decoded_data:
            return None
        return decoded_data

    @staticmethod
    def get_user(user_id):
        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            return None
