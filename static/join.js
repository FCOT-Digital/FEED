Vue.createApp({
	data() {
		return {
			joinCode: '',
			sessionId: null,
			comment: '',
		}
	},
	methods: {
		async joinSession() {
			const response = await fetch(
				'/api/participant',
				{
					method: 'POST',
					body: this.joinCode,
				}
			);
			if (response.ok) {
				this.sessionId = await response.text();
			}
		},
		async sendComment() {
			const response = await fetch(
				'/api/comment/' + this.sessionId,
				{
					method: 'PUT',
					body: this.comment,
				}
			);
			if (response.ok) {
				this.comment = '';
			}
		},
	}
}).mount('#app')