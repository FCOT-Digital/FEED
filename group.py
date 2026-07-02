from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def similarities(needle, haystack):
	embeddings = model.encode(
		[needle] + haystack,
		normalize_embeddings=True,
	)
	needle_embedding = embeddings[0]
	haystack_embeddings = embeddings[1:]
	similarities = [
		util.cos_sim(needle_embedding, haystack_embedding).item()
		for haystack_embedding in haystack_embeddings
	]
	return similarities

if __name__ == "__main__":
	needle = "This is a test"
	haystack = [
		"This is a test",
		"This is another test",
		"This is a different test",
	]
	similarities = similarities(needle, haystack)
	print(similarities)