from typing import Dict, Union, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from statistics import harmonic_mean
from sentence_transformers import SentenceTransformer
import numpy as np
import numpy.typing as npt
import pandas as pd


class RuleBasedSentiment(object):
    def __init__(self) -> None:
        self.analyzer = SentimentIntensityAnalyzer()

    def get_valence_dict(self, query: str) -> Dict[str, float]:
        response = self.analyzer.polarity_scores(query)

        return response

    def get_compound_score(self, query: str) -> float:
        response = self.analyzer.polarity_scores(query)
        score = response.get("compound")

        return score

    def get_positive_score(self, query: str) -> float:
        response = self.analyzer.polarity_scores(query)
        score = response.get("pos")

        return score

    def get_negative_score(self, query: str) -> float:
        response = self.analyzer.polarity_scores(query)
        score = response.get("neg")

        return score

    def get_neutral_score(self, query: str) -> float:
        response = self.analyzer.polarity_scores(query)
        score = response.get("pos")

        return score

    def get_hmean_score(self, query: str) -> float:
        response = self.analyzer.polarity_scores(query)
        scores = []
        for k in response.keys():
            if (
                k != "compound"
                and type(response.get(k)) in [float, int]
                and response.get(k) > 0
            ):
                scores.append(response.get(k))

        return harmonic_mean(scores)


class EmbeddedSentiment(object):
    def __init__(self, model_name="all-mpnet-base-v2") -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

    def create_embeddings(
        self, query: str, normalize: bool = True, progress_bar: bool = False
    ) -> npt.NDArray[np.float_]:
        embeddings = self.model.encode(
            query, normalize_embeddings=normalize, show_progress_bar=progress_bar
        )

        # Ensure vector elements are float32 type.
        embeddings = np.asarray(embeddings, dtype="float32")

        return embeddings

    @staticmethod
    def calc_dot_product(
        vector1: npt.NDArray[np.float_], vector2: npt.NDArray[np.float_]
    ) -> npt.NDArray[np.float_]:

        # Ensure both vectors exist
        if vector1.size == 0 or vector2.size == 0:
            return np.asarray([])
        try:
            vector1.shape[1]
        except IndexError:
            vector1 = np.asarray([vector1])
        try:
            vector2.shape[1]
        except IndexError:
            vector2 = np.asarray([vector2])

        # Dot product of L2 normalized vectors equals the cosine similarity.
        # Staples embeddings will be a (N, 768) vector where N is the number of product names and 768 is the dimension of the embedding based on
        # the model chosen (it could be different based on the model). The target embedding will be (1, 768) since it's an embedding of only
        # one product name. The target embedding will need to be transposed to (768, 1) so the multiplication of, (N, 768) X (768, 1) works out.
        # The resulting dot product will have dimension (N,1) with a cosine similarity for each target product/staples product pair.
        if vector1.shape[1] == vector2.shape[0]:
            dot_product = np.dot(vector1, vector2)
        else:
            dot_product = np.dot(vector1, vector2.T)

        if dot_product.shape[0] == 1:
            dot_product = dot_product[0]

        return dot_product

    @staticmethod
    def get_closest_matches(
        similarity_scores: npt.NDArray[np.float_], limit: int
    ) -> npt.NDArray[np.int_]:
        if len(similarity_scores) < limit:
            limit = len(similarity_scores)
        # Will return the indices of the highest similarity scores (returns N highest where N=limit)
        indices = np.argpartition(similarity_scores, -limit)[-limit:]

        return indices

    @staticmethod
    def get_sentiment_scores(
        indices: npt.NDArray[np.int_],
        sentiment_labels: Union[npt.NDArray[np.int_], List[int]],
    ) -> float:
        # Figures out the sentiment label
        scores_arr = sentiment_labels[indices]
        mean = sum(scores_arr) / len(scores_arr)

        return mean

    def get_stock_data_embed(self, filepath: str, sample: int = 1000) -> pd.DataFrame:

        stock_df = pd.read_csv(filepath_or_buffer=filepath, header=0, index_col=0)
        stock_df = stock_df.sample(n=sample)
        sentences = stock_df["Sentence"].to_numpy()
        embeddings = self.create_embeddings(sentences, progress_bar=True)
        stock_df["Embeddings"] = embeddings.tolist()
        stock_df.reset_index(inplace=True)

        return stock_df


if __name__ == "__main__":
    pass
