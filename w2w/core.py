import logging
import urllib3
import certifi
import pprint
import time
from abc import ABCMeta

from w2w.utils import (
    dic_to_json,
    response_to_dic
)

logger = logging.getLogger(__name__)

def timed(func):
    """
    Decorator to log execution time of decorated methods methods
    """

    _logger = logging.getLogger(__name__ + '.Timed')

    def wrapped(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        methodName = type(args[0]).__name__ + '.' + func.__name__
        _logger.info('Executed {method} in {time} seconds.'
        .format(method=methodName, time=(time.time() - start)))
        return(res)

    return wrapped

class Resource(object):
    """Abstract resource class.

    Works as a base class for all other resources, keeping the generic and re-usable functionality.

    Provides to the classes that inherit it with a connection pool (:any:`urllib3.connectionpool.HTTPSConnectionPool`)
    and methods to make requests to the anilist api through it.

    All resources **must** be singletons.

    The only request this class doesn't handle are the authentication ones, managed by :any:`AuthenticationProvider`

    """

    _URL = 'https://graphql.anilist.co'
    _METHOD = 'POST'
    _ENDPOINT = '/'
    _HEADERS = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def __init__(self):
        self._pool = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).connection_from_url(Resource._URL)


    def __new__(type):
        if not '_instance' in type.__dict__:
            type._instance = object.__new__(type)
        return type._instance


    @timed
    def execute(self, query, variables):
        """
        Executes a GraphQL query against anilist api
        """

        headers = Resource._HEADERS
        endpoint = Resource._ENDPOINT
        method = Resource._METHOD
        data = dic_to_json({'query': query, 'variables': variables})

        logger.debug('Resource request: %s %s' % (method, endpoint))
        logger.debug('Resource request body: %s' % str(data))
        logger.debug('Resource request headers: %s' % headers)

        response = self._pool.request(
            method,
            endpoint,
            body=data,
            headers=headers)

        response = response_to_dic(response)
        logger.debug('Resource response: \n' + pprint.pformat(response))
        return response


class Entity(metaclass=ABCMeta):
    """Abstract base class for al classes that are mapped from/to an anilist response."""

    __composite__ = {}
    """Define how different implementations of this class compose each other. See :any:`fromResponse`"""
    _resource = None

    def __init__(self, **kwargs):
        # TODO: see if i can remove keyword args
        """
        All sub classes **must** override this method. Here is where the json response from the api, converted to a dict
        is mapped to the private attributes of each implementation.

        Implementation example::

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._id = kwargs.get('id')
                self._displayName = kwargs.get('displayName')

        :param kwargs: dict with values from the json entity to be mapped.
        """
        super().__init__()

    @classmethod
    def fromResponse(cls, response):
        """
        Class method that creates an instance of the implementation class, based on a json :obj:`requests.Response` or
        a :obj:`dict`.

        The 'magic' here resides in :any:`__composite__` attribute. :any:`__composite__` is a :obj:`dict` that allow an
        implementation class to define: each time you find, lets say, 'user' in the json response, take its value pass
        it as a parameter of the `fromResponse` method of User class. For this particular example, un the class that
        uses User, you **must** define::

            __composite__ = {'user': User}

        :param response: Base data to create the instance
        :return: An instance of the implementation class, composed and populated with the response data.
        """

        if isinstance(response, urllib3.response.HTTPResponse):
            response = response_to_dic(response)
        dic = {}

        if response['data']:
            response = response['data'][cls.__name__]

        for k in response:
            if k in cls.__composite__:
                dic[k] = cls.__composite__[k].fromResponse(response.get(k))
            else:
                dic[k] = response.get(k)

        logger.debug('Mapped dict: \n' + pprint.pformat(dic))
        return cls(**dic)

