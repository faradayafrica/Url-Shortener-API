from rest_framework_simplejwt.tokens import TokenError, UntypedToken

class TokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            try:
                # Decode the token without any verification or validation
                decoded_token = UntypedToken(token)
                # Retrieve the user information from the token payload
                user_id = decoded_token['user_id']
                # Attach the user information to the request object
                request.user_id = user_id
            except TokenError:
                # Handle token decoding errors
                pass
        else:
            # Handle the case when no token is present
            request.user_id = None

        return self.get_response(request)
