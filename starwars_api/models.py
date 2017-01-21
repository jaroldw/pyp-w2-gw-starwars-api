from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """

        for k, v in json_data.items():
            setattr(self, k, v)  # setattr(x, 'foobar', 123) == x.foobar = 123

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """

        if cls.RESOURCE_NAME == "people":
            json_data = api_client.get_people(resource_id)
            return People(json_data)
        if cls.RESOURCE_NAME == "film":
            json_data = api_client.get_films(resource_id)
            return Film(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """

        if cls.RESOURCE_NAME == "people":
            return PeopleQuerySet()
        if cls.RESOURCE_NAME == "film":
            return FilmsQuerySet()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    """
    def get_people(self, people_id=None, **params):
        if people_id:
            return self._get_swapi('/api/people/{}'.format(people_id))
        return self._get_swapi('/api/people', **params)
    """

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        page_data = self._get_page_records()
        self.total_records = page_data['count']
        self.collected = -1
        self.counter = -1
        self.page = 1
        self.records = page_data['results']

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """

        while True:
            self.counter += 1
            self.collected += 1

            if self.collected == self.total_records:
                raise StopIteration
            if self.counter > len(self.records) - 1:
                # get next page records and reset counter
                self.page += 1
                page_data = self._get_page_records(page_number=self.page)
                self.records = page_data['results']
                self.counter = 0

            return People(self.records[self.counter])

    next = __next__

    def _get_page_records(self, page_number=1):
        if self.RESOURCE_NAME == 'people':
            json_data = api_client.get_people(**{'page': page_number})
        if self.RESOURCE_NAME == 'films':
            json_data = api_client.get_films(**{'page': page_number})

        return json_data

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """

        return len([item for item in self])


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
