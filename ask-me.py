from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from flask import Flask, request
from uuid import uuid4

model = SentenceTransformer("all-MiniLM-L6-v2")
app = Flask(__name__)
participants = {}
join_code = "1234"

@app.route("/")
def index():
	return app.send_static_file("join.html")

@app.route("/api/participant", methods=["POST"])
def create_participant():
	given_code = request.get_data().decode('utf-8')
	if given_code == join_code:
		participant_id = str(uuid4())
		participants[participant_id] = None
		return participant_id
	return "Invalid join code", 400

@app.route("/api/comment/<participant_id>", methods=["PUT"])
def update_comment(participant_id):
	comment = request.get_data().decode('utf-8')
	if participant_id in participants:
		participants[participant_id] = comment
		return participant_id
	return "Invalid participant ID", 400

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
