from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer('roberta-large-nli-stsb-mean-tokens')
torch.save(model, 'model_file')
