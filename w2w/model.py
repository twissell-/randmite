from w2w.core import (
    Entity,
    Resource
)

class User(Entity):
    """
    Object representation of an Anilist User response.
    """

    _resource = Resource()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = kwargs.get('id')
        self._name = kwargs.get('name')

    def __repr__(self):
        return 'User: {id} "{name}"'.format(id=self._id, name=self._name)


    @classmethod
    def resource(cls):
        return cls._resource

    @classmethod
    def byName(cls, name):
        query = '''
        query($userName: String) {
          User(name: $userName) {
            id
            name
          }
        }'''

        variables = {
            'userName': name
        }

        return cls.fromResponse(cls._resource.execute(query, variables))

    @property
    def id(self):
        return self._id

    @property
    def displayName(self):
        return self._displayName
