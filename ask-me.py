from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from flask import Flask, request
from uuid import uuid4

model = SentenceTransformer("all-MiniLM-L6-v2")
app = Flask(__name__)
sessions = {}
join_code = "1234"

@app.route("/")
def index():
	return app.send_static_file("join.html")

@app.route("/api/join", methods=["POST"])
def join_session():
	data = request.get_json()
	if data.get("code") == join_code:
		session_id = str(uuid4())
		sessions[session_id] = None
		return {"session_id": session_id}
	return {"error": "Invalid code"}, 400

def group_by_meaning(sentences, threshold=0.25):
	embeddings = model.encode(sentences, normalize_embeddings=True)
	labels = AgglomerativeClustering(
		n_clusters=None,
		distance_threshold=threshold,
		metric="cosine",
		linkage="average"
	).fit_predict(embeddings)
	grouped_sentences = {}
	for sentence, label in zip(sentences, labels):
		if label not in grouped_sentences:
			grouped_sentences[label] = []
		grouped_sentences[label].append(sentence)
	return list(grouped_sentences.values())

if __name__ == "__main__":
	sentence_examples = [
		"Hello World!",
		"Hello everyone!",
		"Test this.",
	]
	sentence_groups = group_by_meaning(sentence_examples)
	print(sentence_groups)
	app.run()
