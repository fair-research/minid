

def validate_globus_user(email, authorization_header):
    try:
        type, code = authorization_header.split()
        if str(type) != 'Bearer':
            raise AuthorizationException('Only Bearer tokens are supported '
                                         'for Globus Auth',
                                         user=email, type='InvalidToken')

        import globus_sdk  # noqa
        ac = globus_sdk.AuthClient(
            authorizer=globus_sdk.AccessTokenAuthorizer(code))

        try:
            idents = ac.get_identities(email).get('identities')
            if not idents:
                raise AuthorizationException('User needs to link their email '
                                             '%s to their Globus identity: '
                                             'globus.org/app/account' % email,
                                             user=email,
                                             type='InvalidIdentity')
        except globus_sdk.exc.AuthAPIError:
            raise AuthorizationException('Expired or invalid Globus Auth '
                                         'code.', user=email,
                                         type='AuthorizationFailed')
    except (ValueError, AttributeError):
        raise AuthorizationException('Invalid Globus Authorization Header.',
                                     user=email,
                                     type='InvalidHeader')
    except ImportError:
        print('Please install Globus: "pip install globus_sdk"')
        raise AuthorizationException('Server is misconfigured to use '
                                     'Globus Auth, please notify '
                                     'the administrator. Sorry.', user=email,
                                     code=500, type='ServerError')


class AuthorizationException(Exception):
    def __init__(self, message, errors=None, user=None, code=401,
                 type='AuthorizationFailed'):
        super(AuthorizationException, self).__init__(message)
        self.message = message
        self.user = user
        self.code = code
        self.type = type
