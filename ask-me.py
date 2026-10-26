from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from flask import Flask, request, Response
from uuid import uuid4
from datetime import datetime

model = SentenceTransformer("all-MiniLM-L6-v2")
app = Flask(__name__)
participants = {}
grouped_comments = []
updated = datetime.now()
join_code = "1234"

@app.route("/")
def index():
	return app.send_static_file("chat.html")

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
		raw_comments = [comment for comment in participants.values()]
		meaningful_comments = [
			comment for comment in raw_comments
			if comment and len(comment.strip()) > 0
		]
		grouped_comments = group_by_meaning(meaningful_comments)
		updated = datetime.now()
		return participant_id
	return "Invalid participant ID", 400

@app.route("/stream/comment", methods=["GET"])
def stream_comments():
	def stream():
		sent = None
		while True:
			if (
				sent is None or
				updated > sent or
				(datetime.now() - sent).total_seconds() > 7
			):
				sent = datetime.now()
				yield f"data: {grouped_comments}\n\n"
	return Response(stream(), mimetype='text/event-stream')

def group_by_meaning(sentences, threshold=0.25):
	if len(sentences) == 0:
		return []
	elif len(sentences) == 1:
		return [sentences]
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
