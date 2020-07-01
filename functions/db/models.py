from pymodm import fields, MongoModel, EmbeddedMongoModel


class Result(MongoModel):
    # "doi": "The DOI of the record",
    doi = fields.CharField(primary_key=True)

    scores = fields.EmbeddedDocumentListField('Score')

    persisted = fields.BooleanField(required=True)

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
    # "publisher": "Name of the publisher",
    publisher = fields.CharField(blank=True)
    # "publicationDate": "Date of publication",
    publicationDate = fields.CharField(blank=True)
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

    class Meta:
        ignore_unknown_fields = True


class Score(EmbeddedMongoModel):
    # username = fields.CharField()
    username = fields.ReferenceField('User')
    score = fields.IntegerField()
    comment = fields.CharField()


class Review(MongoModel):
    name = fields.CharField()
    owner = fields.ReferenceField('User')
    result_collection = fields.CharField()
    date_created = fields.DateTimeField()
    description = fields.CharField()
    queries = fields.EmbeddedDocumentListField('Query')


class Query(EmbeddedMongoModel):
    _id = fields.ObjectIdField(primary_key=True)
    parent_review = fields.ReferenceField('Review')
    time = fields.CharField()
    results = fields.ListField()
    search = fields.EmbeddedDocumentField('Search')


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
    token = fields.CharField()