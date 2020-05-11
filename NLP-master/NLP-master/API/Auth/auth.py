import sqlite3

from flask import Flask, request
from flask_restful import Resource, Api
import logging
import json
import argparse



LOGGER_NAME = 'auth.log'
DATABASE_NAME = ':memory:'


logger = logging.getLogger(LOGGER_NAME)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



class AuthenticationApi(Resource):


    ERROR_CODE = 400

    '''
    Input:
        grant_type=password - This tells the server we’re using the Password grant type
        username= - The user’s username that they entered in the application
        password= - The user’s password that they entered in the application
        client_id= - The public identifier of the application that the developer obtained during registration
        client_secret= - (optional) - If the application is a “confidential client” (not a mobile or JavaScript app), then the secret is included as well.

    Output:
        access_token: Token provided by generator
        token_type: Token type. "bearer",
        expires_in: Duration time in seconds. "3600"
        scope: Scopes allowed by token. "create"
        refresh_token (optional): Token provided for refreshing
    '''
    def __init__(self, connection, queries):
        self.connection = connection
        self.queries = queries

    def post(self, username, password, client_id, client_secret):
        logger.info('Authentication API working')
        return 'Authentication API working'

    def get(self):
        return 'Authentication API working'


class AuthorizationApi(Resource):

    ERROR_CODE = 400

    def __init__(self, connection, queries):
        self.connection = connection
        self.queries = queries

    def post(self, username, password, client_id, client_secret):
        logger.info('Authorization API working')
        return 'Authorization API working'

    def get(self):
        return 'Authorization API working'




def read_queries(filename):
    with open(filename, 'r') as f:
        queries = json.load(f)

    return queries


def create_database(connection, queries):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(queries['CREATE_LOG_TABLE_QUERY'])
    cursor.execute(queries['CREATE_USER_TABLE_QUERY'])
    cursor.execute(queries['CREATE_TOKEN_TABLE_QUERY'])
    cursor.execute(queries['CREATE_SCOPE_TABLE_QUERY'])
    cursor.execute(queries['CREATE_USER_SCOPE_TABLE_QUERY'])
    
    connection.commit()



def run_api(connection, queries, host='0.0.0.0', port='3706'):
    
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(
        AuthenticationApi, 
        '/authentication/',
        resource_class_kwargs={ 'connection': connection, 'queries': queries }
    )

    api.add_resource(
        AuthorizationApi, 
        '/authorization/',
        resource_class_kwargs={ 'connection': connection, 'queries': queries }
    )

    app.run(host=host, port=port)
    





def main():
    parser = argparse.ArgumentParser()

    ## Required parameters
    parser.add_argument('--queries_file',
                        default=None,
                        type=str,
                        required=True,
                        help='The file where querieas are read from')
    parser.add_argument('--host', 
                        type=str, 
                        default='localhost',
                        help='host where the service will run')
    parser.add_argument('--port', 
                        type=int, 
                        default=5000,
                        help='port where the service will run')
    parser.add_argument('--log_file', 
                        type=str, 
                        default=None,
                        help='File where log')
    parser.add_argument('--log_level',
                        default='INFO',
                        type=str,
                        choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Log level.')
    
    args = parser.parse_args()

    if args.log_file is not None:
        file_handler = logging.handlers.RotatingFileHandler(args.log_file, maxBytes=10000, backupCount=1)
        logger.addHandler(file_handler)
        logger.setLevel(args.log_level)


    connection = sqlite3.connect(DATABASE_NAME)
    queries = read_queries(args.queries_file)
    create_database(connection, queries)
    run_api(connection, queries, host=args.host, port=args.port)

    

if __name__ == "__main__":
    main()





