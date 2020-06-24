from pymodm import fields, MongoModel, EmbeddedMongoModel


class Review(MongoModel):
    name = fields.CharField()
    owner = fields.ReferenceField('User')
    date_created = fields.DateTimeField()
    description = fields.CharField()
    search = fields.EmbeddedDocumentField('Search')
    queries = fields.EmbeddedDocumentListField('Query')


class Query(EmbeddedMongoModel):
    _id = fields.ObjectIdField(primary_key=True)
    time = fields.DateTimeField()


class Search(EmbeddedMongoModel):
    search_groups = fields.EmbeddedDocumentListField('SearchGroup')
    match = fields.CharField(choices=("AND", "OR"))


class SearchGroup(EmbeddedMongoModel):
    search_terms = fields.ListField(fields.CharField())
    match = fields.CharField(choices=("AND", "OR", "NOT"))


class User(MongoModel):
    username = fields.CharField(primary_key=True)
    name = fields.CharField()
    surname = fields.CharField()
    email = fields.CharField()
    password = fields.CharField()
    databases = fields.EmbeddedDocumentListField('DatabaseInfo')


class DatabaseInfo(EmbeddedMongoModel):
    db_name = fields.CharField()
    api_key = fields.CharField()


class UserSession(MongoModel):
    username = fields.CharField(primary_key=True)
    jwt = fields.CharField()


class Result(MongoModel):
    review = fields.ReferenceField('Review')
    queries = fields.ListField()

    scores = fields.EmbeddedDocumentListField('Score')

    # "contentType": "Type of the content (e.g. Article)",
    contentType = fields.CharField(blank=True)
    # "title": "The title of the record",
    title = fields.CharField(blank=True)
    # "authors": ["Full name of one creator"],
    authors = fields.ListField(blank=True)
    # "publicationName": "Name of the publication",
    publicationName = fields.CharField(blank=True)
    # "openAccess": "Bool: Belongs to openaccess collection",
    openAccess = fields.BooleanField(blank=True)
    # "doi": "The DOI of the record",
    doi = fields.CharField(blank=True)
    # "publisher": "Name of the publisher",
    publisher = fields.CharField(blank=True)
    # "publicationDate": "Date of publication",
    publicationDate = fields.DateTimeField(blank=True)
    # "publicationType": "Type of publication",
    publicationType = fields.CharField(blank=True)
    # "issn": "International Standard Serial Number",
    issn = fields.CharField(blank=True)
    # "volume": "Volume of the publication",
    volume = fields.CharField(blank=True)
    # "number": "Number of the publication",
    number = fields.CharField(blank=True)
    # "genre": ["Name of one genre"],
    genre = fields.ListField(blank=True)
    # "pages": {
    #     "first": "First page in publication",
    #     "last": "Last page in publication"
    # },
    pages = fields.ListField(blank=True)
    # "journalId": "ID of the publication journal",
    journalId = fields.CharField(blank=True)
    # "copyright": "Copyright notice",
    copyright = fields.CharField(blank=True)
    # "abstract": "Abstract (Summary)",
    abstract = fields.CharField(blank=True)
    # "uri": "Link to the record"
    uri = fields.CharField(blank=True)
    #
    printIsbn = fields.CharField(blank=True)
    electronicIsbn = fields.CharField(blank=True)
    isbn = fields.CharField(blank=True)


class Score(EmbeddedMongoModel):
    user = fields.ReferenceField('User')
    score = fields.IntegerField()
    comment = fields.CharField()
