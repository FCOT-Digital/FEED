Vue.createApp({
	data() {
		return {
			commentStream: null,
			sessionId: '',
			participantId: null,
			comment: '',
			comments: [],
		}
	},
	methods: {
		async joinSession() {
			if (this.commentStream) {
				this.commentStream.close();
			}
			this.comments = [];
			this.comment = '';
			this.commentStream = new EventSource(
				'/stream/session/' + this.sessionId + '/comment'
			);
			this.commentStream.onmessage = (event) => {
				this.comments = JSON.parse(event.data);
			};
			const participant = await fetch(
				'/api/session/' + this.sessionId + '/participant',
				{ method: 'POST' }
			);
			if (participant.ok) {
				this.participantId = await participant.text();
			}
		},
		async sendComment() {
			url = [
				'api/session',
				this.sessionId,
				'participant',
				this.participantId,
				'comment',
			].join('/');
			payload = {
				method: 'PUT',
				body: this.comment,
			}
			const response = await fetch(url, payload);
			if (response.ok) {
				this.comment = '';
			}
		},
	},
	unmounted() {
		if (this.commentStream) {
			this.commentStream.close();
		}
	},
}).mount('#app')