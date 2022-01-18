from imports import *
from rewrite.PreProcessorBert import PreProcessorBert
import numpy as np

class PreProcessorSBert(PreProcessorBert):
    def __init__(self):
        super().__init__()
        self.sentenceTransformer = SentenceTransformer('paraphrase-distilroberta-base-v1')

    # Get the embeddings correlated to the text
    def emb_tokenizer(self, text):
        sentence = self.split_sentences(text)
        embedding = self.sentenceTransformer.encode(sentence)
        return embedding

    def create_fields(self):
        EMBEDDING = data.Field(sequential = True, 
            batch_first = True,
            tokenize = self.emb_tokenizer, 
            use_vocab = False,
            dtype= torch.float
            )
        return np.concatenate([super().create_fields(), [('embedding', EMBEDDING)]])