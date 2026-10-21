from sentence_transformers import SentenceTransformer, util

def group_by_meaning(sentences):
	model = SentenceTransformer("all-MiniLM-L6-v2")
	embeddings = model.encode(sentences, normalize_embeddings=True)
	similarities = model.similarity(embeddings, embeddings)
	print(similarities)
	print(similarities.mean())
	print(similarities.std())
	

if __name__ == "__main__":
	sentence_examples = [
		"Hello World!",
		"Hello everyone!",
		"Test this.",
	]
	sentence_groups = group_by_meaning(sentence_examples)
