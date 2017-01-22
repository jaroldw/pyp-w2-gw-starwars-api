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
        
        # this seems to work. not sure if this is valid or a "hack"
        return eval(cls.__name__ + 'QuerySet')()


        # # this is what we had before
        # if cls.RESOURCE_NAME == "people":
        #     return PeopleQuerySet()

        # if cls.RESOURCE_NAME == "films":
        #     return FilmsQuerySet()

#         # this is what I was experimenting with to compare a variety of results
#         if cls.RESOURCE_NAME == "people":
# #            return PeopleQuerySet()
#             return eval(cls.__name__ + 'QuerySet')()

#         if cls.RESOURCE_NAME == "films":
# #             print(cls)
# #             print(type(cls))
# #             print(cls.__getattribute__)
# #             print(cls.__class__)
# #             print(type(FilmsQuerySet()))
# #             print(cls.__name__)
# #             print(eval(cls.__name__ + 'QuerySet')) # this may work.
# # #            print(cls.get(cls))
# # #            print(cls.all()) # infinite recursion of sorts? times out
# #             print('-'*20)
# #             print(dir(cls))
# # #            return FilmsQuerySet() # this is what works right now.
#             return eval(cls.__name__ + 'QuerySet')()
# #            return cls._get_page_data()
# #            return cls(getattr(api_client, "get_{}".format(cls.RESOURCE_NAME)))

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

            # this has to be a total hack.... but it works for now
            # before, we manually referenced elem = People(self.records[self.counter])
            # however, "self" here is PeopleQueryset. If we can somehow obtain "People" from "self",
            # then we can replace the hack in the next line
            elem = eval((self.RESOURCE_NAME).capitalize())(self.records[self.counter])

            self.counter += 1
            self.collected += 1
            return elem

                
#            elem = eval(self.__class__.__name__)()
            # print(type(elem))
            # print(elem)
            # print('-'*20)
#            elem = eval(self.__class__.__name__)(self.records[self.counter])
#                elem = eval(self.__class__.__name__)(self.records[self.counter]) # TypeError: __init__() takes exactly 1 argument (2 given)
#            elem = eval(self.__class__.__name__)((self.records[self.counter])) # TypeError: __init__() takes exactly 1 argument (2 given)
#            print(type(self._get_page_data()))

#            e2 = eval(self.__class__.__name__)()
#            print(e3)
#            print(type(e2))
#            print(dir(e2))
#            print('-'*20)

            # # this is what we had before
            # if self.RESOURCE_NAME == "people":
            #     elem = People(self.records[self.counter])
            # if self.RESOURCE_NAME == "films":
            #     elem = Films(self.records[self.counter])

            # self.counter += 1
            # self.collected += 1
            # return elem

    next = __next__

    def _get_page_data(self, page_number=1):
        
        # made more general
        return getattr(api_client, "get_{}".format(self.RESOURCE_NAME))(page=page_number)

        # # previously
        # if self.RESOURCE_NAME == 'people':
        #     json_data = api_client.get_people(page=page_number)
        # if self.RESOURCE_NAME == 'films':
        #     json_data = api_client.get_films(page=page_number)
        # return json_data

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
