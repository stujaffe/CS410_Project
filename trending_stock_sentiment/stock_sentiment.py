import flair
import spacy

# python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm')
model = flair.models.TextClassifier.load('en-sentiment')


def get_entities(text):
    doc = nlp(text)
    entities = []
    for entity in doc.ents:
        if entity.label_ == 'ORG':
            entities.append(entity)

    entities = list(set(entities))
    return entities


def get_sentiment(text):
    sen = flair.data.Sentence(text)
    model.predict(sen)
    return str(sen.labels[0].score) + ' ' + sen.labels[0].value


class StockSentiment(object):

    def __init__(self, df):
        self.df = df

    def get_stock_sentiment(self):
        self.df['entities'] = self.df['posts'].apply(get_entities)
        self.df = self.df[self.df['entities'].str.len() > 0]
        self.df['sentiment'] = self.df['posts'].apply(get_sentiment)

        return self.df


if __name__ == "__main__":
    pass
