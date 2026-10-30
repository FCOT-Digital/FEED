from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from flask import Flask, request, Response
from uuid import uuid4
from datetime import datetime
import json

model = SentenceTransformer("all-MiniLM-L6-v2")
app = Flask(__name__)
participants = {}
grouped_comments = []
updated = datetime.now()
join_code = "1234"

@app.route("/")
def index():
	return app.send_static_file("chat.html")

@app.route(
	"/api/session/<session_id>/participant",
	methods=["POST"],
)
def create_participant(session_id):
	global participants
	if session_id != join_code:
		return "Invalid join code", 400
	participant_id = str(uuid4())
	participants[participant_id] = None
	return participant_id

@app.route(
	"/api/session/<session_id>/participant/<participant_id>/comment",
	methods=["PUT"],
)
def update_comment(session_id, participant_id):
	global grouped_comments, updated
	if session_id != join_code:
		return "Invalid join code", 400
	if participant_id not in participants:
		return "Invalid participant ID", 400
	comment = request.get_data().decode('utf-8')
	participants[participant_id] = comment
	raw_comments = [comment for comment in participants.values()]
	meaningful_comments = [
		comment for comment in raw_comments
		if comment and len(comment.strip()) > 0
	]
	grouped_comments = group_by_meaning(meaningful_comments)
	updated = datetime.now()
	return participant_id

@app.route(
	"/stream/session/<session_id>/comment",
	methods=["GET"],
)
def stream_comments(session_id):
	if session_id != join_code:
		return "Invalid join code", 400
	def stream():
		global grouped_comments, updated
		sent = None
		while True:
			if (
				sent is None or
				updated > sent or
				(datetime.now() - sent).total_seconds() > 7
			):
				sent = datetime.now()
				yield f"data: {json.dumps(grouped_comments)}\n\n"
	return Response(stream(), mimetype='text/event-stream')

def group_by_meaning(sentences, threshold=0.6):
	if len(sentences) == 0:
		return []
	if len(sentences) == 1:
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
		"How does the SDLC work when making a video game instead of normal software?",
		"Can you go back to a previous stage in waterfall or do you have to restart?",
		"Why do developers need to make documantation if the code already works?",
		"How do you know when to move onto the next stage of development?",
		"What happens if the client changes there requirements halfway through?",
		"Is Scrum the same thing as agile or are they different?",
		"What does maintanence mean in the SDLC?",
		"Why would a company use waterfall instead of agile if agile is faster?",
		"What is the diffrence between verification and validation?",
		"How many stages are there in the software developement life cycle?",
		"Is testing only done at the end or can you do it during development?",
		"What happens in the planning stage of the SDLC?",
		"Why cant developers just start coding straight away?",
		"Whats the difference between waterfall and agile?",
		"What is the SDLC and why do we actually need it?",
	]
	sentence_groups = group_by_meaning(sentence_examples)
	for group in sentence_groups:
		for sentence in group:
			print(sentence)
		print("---")
	app.run()
