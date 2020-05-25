from pymodm import fields, MongoModel, EmbeddedMongoModel

class Review(MongoModel):
    name = fields.CharField()
    owner = fields.ReferenceField('User')
    search = fields.EmbeddedDocumentField('Search')
    results = fields.EmbeddedDocumentListField('Result')


class Search(EmbeddedMongoModel):
    date = fields.DateTimeField()
    title = fields.CharField()
    concepts = fields.EmbeddedDocumentListField('Concept')
    results = fields.EmbeddedDocumentListField('Result')

class Concept(EmbeddedMongoModel):
    term = fields.CharField()
    field = fields.ListField()
    synonyms = fields.ListField()


class User(MongoModel):
    name = fields.CharField(primary_key=True)


class Result(EmbeddedMongoModel):
    title = fields.CharField()
    subject = fields.CharField(required=False)
    institution = fields.CharField(required=False)
    isbn_10 = fields.CharField(required=False)
    publisher = fields.CharField(required=False)
    published_in = fields.CharField(required=False)
    author = fields.CharField(required=False)
    found_by = fields.ReferenceField('Search', required=False)
    scores = fields.EmbeddedDocumentListField('Score')


class Score(EmbeddedMongoModel):
    user = fields.ReferenceField('User')
    score = fields.IntegerField()
    comment = fields.CharField()

