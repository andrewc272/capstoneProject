let gameState;
let realized_gameState;
let game_HTML;
let users;
let form_shown = false;
let lastChatLength = 0;

async function update_gameState(){
	try {
		const response = await fetch('/gameState');
		if (!response.ok) return;
		gameState = await response.json();
		users = gameState.users || [];
	} catch {
		return;
	}
}

async function update_gameFrame(){
	try {
		const response = await fetch(`/static/${gameState.gamePhase}.html`);
		game_HTML = await response.text();
		realized_gameState = gameState.gamePhase;
		document.getElementById("game").innerHTML = game_HTML;
		lastChatLength = 0;
	} catch {}
}

async function introJS() {
	const joinButton = document.getElementById("join_game");
	if (joinButton && !joinButton.dataset.listenerAdded) {
		joinButton.addEventListener('click', async function() {
			await fetch('/addPlayer');
		});
		joinButton.dataset.listenerAdded = "True";
	}
	const startButton = document.getElementById("start_game");
	if (startButton && !startButton.dataset.listenerAdded) {
		startButton.addEventListener('click', function() {
			fetch('/gameState', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ nextPhase: true })
			});
		});
		startButton.dataset.listenerAdded = "True";
	}
	const myId = gameState.myId;
	const lobby = document.getElementById("lobby_list");
	if (lobby) {
		lobby.innerHTML = `
			${gameState.users.map((user, index) => {
				const isSelf = user === myId;
				const playerClass = isSelf ? 'self-player' : 'other-player';
				const playerLabel = isSelf ? 'You are here!!' : `Player ${index + 1} is here!!`;
				return `<li class="${playerClass}">${playerLabel}</li>`;
			}).join('')}
		`;
	}
}

async function lobbyJS(){
	const startButton = document.getElementById("start_game");
	if (startButton && !startButton.dataset.listenerAdded) {
		startButton.addEventListener('click', function() {
			fetch('/gameState', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ nextPhase: true })
			});
		});
		startButton.dataset.listenerAdded = "True";
	}
	const myId = gameState.myId;
	const lobby = document.getElementById("lobby_list");
	if (lobby) {
		lobby.innerHTML = `
			${gameState.users.map((user, index) => {
				const isSelf = user === myId;
				const playerClass = isSelf ? 'self-player' : 'other-player';
				const playerLabel = isSelf ? 'You are here!!' : `Player ${index + 1} is here!!`;
				return `<li class="${playerClass}">${playerLabel}</li>`;
			}).join('')}
		`;
	}
}

function createChatListIfNeeded() {
	const chatArea = document.getElementById('chat_area');
	if (!chatArea) return null;
	let ul = document.getElementById('chat_list');
	if (!ul) {
		ul = document.createElement('ul');
		ul.id = 'chat_list';
		chatArea.appendChild(ul);
	}
	return ul;
}

async function chatJS(){
	const myId = gameState.myId;
	const chatArea = document.getElementById('chat_area');
	if (!chatArea) return;
	const ul = createChatListIfNeeded();
	if (!ul) return;

	const wasNearBottom = (chatArea.scrollHeight - chatArea.scrollTop - chatArea.clientHeight) < 60;

	const chats = gameState.chats || [];
	const newCount = chats.length;

	if (newCount < lastChatLength) {
		ul.innerHTML = '';
		lastChatLength = 0;
	}

	for (let i = lastChatLength; i < chats.length; i++) {
		const chat = chats[i];
		const isSelf = chat[0] === myId;
		const li = document.createElement('li');
		const userIndex = users.indexOf(chat[0]);
		const playerId = `player${userIndex + 1}`;
		li.id = playerId;
		li.className = isSelf ? 'self-player' : 'other-player';
		li.textContent = chat[1] || '';
		ul.appendChild(li);
	}

	lastChatLength = chats.length;

	if (wasNearBottom) {
		chatArea.scrollTop = chatArea.scrollHeight;
	}

	const form = document.getElementById("textbox_form");
	if (form && !form.dataset.listenerAdded){
		form.addEventListener('submit', function(event) {
			event.preventDefault();
			const formData = new FormData(form);
			const data = {};
			formData.forEach((value, key) => {
				data[key] = value;
			});
			fetch('/message', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(data)
			});
			form.querySelector('#chatbox').value = '';
		});
		form.dataset.listenerAdded = "True";
	}
}

async function guessJS(){
	const myId = gameState.myId;
	const users = gameState.users;
	if (!form_shown) {
		const lobbyDiv = document.getElementById("lobby_list");
		if (lobbyDiv) {
			lobbyDiv.innerHTML = `
				${users.map((userId, index) => {
					const isSelf = userId === myId;
					const labelName = isSelf ? "You" : `Player ${index + 1}`;
					const fieldName = `vote-${userId}`;
					return `
						<div class="player-row">
							<span class="player-name">${labelName}</span>
							<label><input type="radio" name="${fieldName}" value="human" required>Human</label>
							<label><input type="radio" name="${fieldName}" value="ai">AI</label>
						</div>
					`;
				}).join('')}
			`;
		}
		form_shown = true;
	}
	const form = document.getElementById("guess_form");
	if (form && !form.dataset.listenerAdded) {
		form.addEventListener("submit", async function (event) {
			event.preventDefault();
			const formData = new FormData(form);
			const votes = users.map((userId) => {
				const fieldName = `vote-${userId}`;
				const guess = formData.get(fieldName);
				return { target: userId, guess: guess };
			});
			await fetch("/vote", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ votes })
			});
			Array.from(form.elements).forEach(e => e.disabled = true);
		});
		form.dataset.listenerAdded = "True";
	}
}

async function resultsJS() {
    const myId = gameState.myId;
    const users = gameState.users;
    const players = gameState.players || [];
    const container = document.getElementById("results_container");
    if (!container) return;

    // Build vote lookup
    const votesById = {};
    players.forEach(p => votesById[p.user_id] = p.votes);

    const maxVotes =
        players.length > 0 ? Math.max(...players.map(p => p.votes)) : 0;

    // Bots (these exist in players[], may not exist in users[])
    const bots = players.filter(p => p.is_a_bot);

    container.innerHTML = `
        <ul class="results-list">
            ${users.map((userId, index) => {
                const isSelf = userId === myId;
                const displayName = isSelf ? "You" : `Player ${index + 1}`;
                const votes = votesById[userId] || 0;
                const isWinner = votes === maxVotes && maxVotes > 0;
                const liClass = isWinner ? "result-row winner" : "result-row";
                return `
                    <li class="${liClass}">
                        <span class="player-name">${displayName}</span>
                        <span class="player-votes">${votes} vote${votes === 1 ? "" : "s"}</span>
                    </li>
                `;
            }).join("")}
        </ul>

        <div class="bot-reveal">
            <h3>Bots in This Game</h3>
            <ul>
                ${bots.map(b => {
                    // Find bot's index based on players[] ordering
                    const idx = players.findIndex(p => p.user_id === b.user_id);
                    const displayName =
                        b.user_id === myId ? "You (Bot)" : `Player ${idx + 1}`;
                    return `<li>${displayName}</li>`;
                }).join("")}
            </ul>
        </div>
    `;
}

async function updateGame(){
	await update_gameState();
	if (!gameState) return;
	if (gameState.gamePhase != realized_gameState ){
		await update_gameFrame();
	}
	if (gameState.gamePhase == "intro") introJS();
	else if (gameState.gamePhase == "lobby") lobbyJS();
	else if (gameState.gamePhase == "chat") chatJS();
	else if (gameState.gamePhase == "guess") guessJS();
	else if (gameState.gamePhase == "results") resultsJS();
}

setInterval(updateGame, 500);


