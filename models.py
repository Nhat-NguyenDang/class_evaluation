"""# Import Model"""
import transformers
import sentence_transformers
# transformers.BertTokenizer = transformers.BertJapaneseTokenizer
from sentence_transformers import SentenceTransformer
from sentence_transformers import models, datasets, losses

def build_model(model_path):
    bert = models.Transformer(model_path)
    pooling = models.Pooling(
            bert.get_word_embedding_dimension(),
            pooling_mode_mean_tokens=True,
    )

    model = SentenceTransformer(modules=[bert, pooling])
    return model