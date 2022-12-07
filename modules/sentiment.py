from typing import Dict, Union, List, Tuple
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from statistics import harmonic_mean
from sentence_transformers import SentenceTransformer
import numpy as np
import numpy.typing as npt


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
        self, query: str, normalize: bool = True
    ) -> npt.NDArray[np.float_]:
        embeddings = self.model.encode(query, normalize_embeddings=normalize)

        # Ensure vector elements are float32 type.
        embeddings = np.asarray(embeddings, dtype="float32")

        return embeddings

    def calc_dot_product(
        vector1: npt.NDArray[np.float_], vector2: npt.NDArray[np.float_]
    ) -> npt.NDArray[np.float_]:

        # Ensure both vectors exist
        if vector1.size == 0 or vector2.size == 0:
            return np.asarray([])

        # Dot product of L2 normalized vectors equals the cosine similarity.
        # Staples embeddings will be a (N, 768) vector where N is the number of product names and 768 is the dimension of the embedding based on
        # the model chosen (it could be different based on the model). The target embedding will be (1, 768) since it's an embedding of only
        # one product name. The target embedding will need to be transposed to (768, 1) so the multiplication of, (N, 768) X (768, 1) works out.
        # The resulting dot product will have dimension (N,1) with a cosine similarity for each target product/staples product pair.
        if vector1.shape[1] == vector2.shape[0]:
            dot_product = np.dot(vector1, vector2)
        else:
            dot_product = np.dot(vector1, vector2.T)

        # We want the resulting vector to have N rows and 1 column. If it has 1 row (shape[0]) and N columns (shape[1]) then we won't be able
        # to index it properly. That is, dot_product[4] with dot_product having shape (1, N) would throw an exception because all the results
        # are stored column-wise, not row-wise.
        if dot_product.shape[0] < dot_product.shape[1]:
            dot_product = dot_product.T

        return dot_product

    def get_closest_matches(
        similarity_scores: npt.NDArray[np.float_], limit: int
    ) -> npt.NDArray[np.int_]:
        # Will return the indices of the highest similarity scores (returns N highest where N=limit)
        indices = np.argpartition(similarity_scores, -limit)[-limit:]

        return indices

    def get_sentiment_scores(
        indices: npt.NDArray[np.int_],
        sentiment_labels: Union[npt.NDArray[np.int_], List[int]],
    ) -> Tuple[bool, float]:
        # Figures out the sentiment label
        scores_arr = sentiment_labels[indices]
        mean = sum(scores_arr)/len(scores_arr)
        if mean > 0.5:
            label = 1
        elif mean == 0.5:
            label = 0
        else:
            label = -1

        return (
            label,
            mean,
        )


if __name__ == "__main__":
    pass
