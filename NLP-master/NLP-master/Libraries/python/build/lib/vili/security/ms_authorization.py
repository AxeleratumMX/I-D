from jwt import JWT, jwk_from_pem
from functools import wraps
from flask import request, abort
import logging

SCOPE_CLAIM = 'sc'

def log(logger, log_level, message):
    if logger is not None:
        logger.log(log_level, message)

def requires_authorization(scope, decrypt_key, logger=None):
    
    if scope is None:
        log(logger, logging.ERROR, 'Current scope must be specified.')
        raise ValueError('Current scope must be specified.')

    if decrypt_key is None:
        log(logger, logging.ERROR, 'Decrypt key must be specified.')
        raise ValueError('Decrypt key must be specified.')

  
    decoder = JWT()
    verifying_key = jwk_from_pem(decrypt_key)

    def inner_function(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if request.headers.get('authorization') is None:
                log(logger, logging.ERROR, 'Authorization code not provided.')
                return abort(401, 'Authorization code not provided.')

            authorization_header = request.headers['Authorization'].split(' ')

            if len(authorization_header) != 2:
                log(logger, logging.ERROR, 'Invalid Authorization JWT format.')
                return abort(403, 'Invalid Authorization JWT format.')

            if authorization_header[0].lower().strip() != 'bearer':
                log(logger, logging.ERROR, 'Invalid Authorization type.')
                return abort(403, 'Invalid Authorization type.')

            jwt = authorization_header[1]

            try:
                payload = decoder.decode(jwt, verifying_key)
            except:
                log(logger, logging.ERROR, 'Invalid JWT.')
                return abort(403, 'Invalid JWT.')
        
            # Here all validations

            # Validate JWT is not expired
            # return abort(401, 'JWT expired')

            # Validate the inclusion of scope in JWT  
            if SCOPE_CLAIM in payload.keys():

                allowed_scopes = [ scope.strip() for scope in payload[SCOPE_CLAIM].split(',') ]

                if scope not in allowed_scopes:
                    log(logger, logging.ERROR, 'This scope is not allowed.')
                    return abort(403, 'This scope is not allowed.')
            else:
                log(logger, logging.ERROR, 'Scopes not included in JWT.')
                return abort(403, 'Scopes not included in JWT.')

            
            log(logger, logging.INFO, 'Authorization OK.')
            return function(*args, **kwargs)

        return wrapper

    return inner_function
