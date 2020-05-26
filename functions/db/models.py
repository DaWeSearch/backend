from pymodm import fields, MongoModel, EmbeddedMongoModel

class Review(MongoModel):
    name = fields.CharField()
    owner = fields.ReferenceField('User')
    search = fields.EmbeddedDocumentField('Search')
    results = fields.EmbeddedDocumentListField('Result')


class Search(EmbeddedMongoModel):
    date = fields.DateTimeField()
    concepts = fields.EmbeddedDocumentListField('Concept')


class Concept(EmbeddedMongoModel):
    term = fields.CharField()
    synonyms = fields.ListField()


class User(MongoModel):
    name = fields.CharField(primary_key=True)


class Result(EmbeddedMongoModel):
    title = fields.CharField()
    author = fields.CharField()
    found_by = fields.ReferenceField('Search', required=False)
    scores = fields.EmbeddedDocumentListField('Score')


class Score(EmbeddedMongoModel):
    user = fields.ReferenceField('User')
    score = fields.IntegerField()
    comment = fields.CharField()


class Book(Result):
    isbn_10 = fields.CharField()


class JournalArticle(Result):
    pass