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
			const response = await fetch(
				'/api/session/' + this.sessionId + '/participant/' + this.participantId + '/comment',
				{
					method: 'PUT',
					body: this.comment,
				}
			);
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