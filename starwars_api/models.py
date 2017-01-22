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

        return cls(getattr(api_client, "get_{}".format(cls.RESOURCE_NAME))(resource_id))

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """

        return eval(cls.__name__ + 'QuerySet')()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

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
        page_data = self._get_page_data()
        self.total_records = page_data['count']
        self.records = page_data['results']

        self.collected = 0
        self.counter = 0
        self.page = 1  # page index starts at 1

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """

        while True:
            if self.collected == self.total_records:
                raise StopIteration
            if self.counter > len(self.records) - 1:
                # get next page records and reset counter
                self.page += 1
                page_data = self._get_page_data(page_number=self.page)

                self.records = page_data['results']
                self.counter = 0

            elem = eval((self.RESOURCE_NAME).capitalize())(
                self.records[self.counter])

            self.counter += 1
            self.collected += 1
            return elem

    next = __next__

    def _get_page_data(self, page_number=1):

        # made more general
        return getattr(api_client, "get_{}".format(self.RESOURCE_NAME))(page=page_number)

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
