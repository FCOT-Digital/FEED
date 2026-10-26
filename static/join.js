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
		const response = await fetch('/api/join', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				code: this.joinCode
			})
		});
		const data = await response.json();
		if (data.session_id) {
			this.sessionId = data.session_id;
		}
	},
	async sendComment() {
		await fetch('/api/comment', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				session_id: this.sessionId,
				comment: this.comment
			})
		});
		this.comment = '';
	},
  }
}).mount('#app')