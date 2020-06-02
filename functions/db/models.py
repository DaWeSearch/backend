from pymodm import fields, MongoModel, EmbeddedMongoModel


class Review(MongoModel):
    name = fields.CharField()
    owner = fields.ReferenceField('User')
    search = fields.EmbeddedDocumentField('Search')
    results = fields.EmbeddedDocumentListField('Result')
    date_created = fields.DateTimeField()


class Search(EmbeddedMongoModel):
    search_groups = fields.EmbeddedDocumentListField('SearchGroup')
    match_and_or = fields.CharField(choices=("AND", "OR"))


class SearchGroup(EmbeddedMongoModel):
    search_terms = fields.ListField(fields.CharField())
    match_and_or_not = fields.CharField(choices=("AND", "OR", "NOT"))


class User(MongoModel):
    name = fields.CharField(primary_key=True)


class Result(EmbeddedMongoModel):
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

    found_by = fields.ReferenceField('Search', required=False)
    scores = fields.EmbeddedDocumentListField('Score')


class Score(EmbeddedMongoModel):
    user = fields.ReferenceField('User')
    score = fields.IntegerField()
    comment = fields.CharField()