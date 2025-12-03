let gameState;
let realized_gameState;
let game_HTML;
let users;
let form_shown = false;
let lastChatLength = 0;
let hostSettings = { botMode: "cloud_api", localModel: null, localBotCount: 1 };
let modelOptions = [];
let hostConfigTimer = null;

async function update_gameState(){
	try {
		const response = await fetch('/gameState');
		if (!response.ok) return;
		gameState = await response.json();
		users = gameState.users || [];
		modelOptions = gameState.modelOptions || [];
		syncHostSettingsFromState();
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

function syncHostSettingsFromState() {
	if (!gameState) return;
	if (gameState.botMode) {
		hostSettings.botMode = gameState.botMode;
	}
	if (gameState.localModel) {
		hostSettings.localModel = gameState.localModel;
	}
	if (typeof gameState.localBotCount !== 'undefined') {
		const parsed = parseInt(gameState.localBotCount, 10);
		if (!Number.isNaN(parsed) && parsed > 0) {
			hostSettings.localBotCount = parsed;
		}
	}
	if (!hostSettings.localModel && modelOptions.length > 0) {
		hostSettings.localModel = modelOptions[0].id;
	}
	if (modelOptions.length > 0 && !modelOptions.some(opt => opt.id === hostSettings.localModel)) {
		hostSettings.localModel = modelOptions[0].id;
	}
}

function persistHostSettings() {
	if (!gameState || !gameState.isHost) return;
	if (hostConfigTimer) {
		clearTimeout(hostConfigTimer);
	}
	hostConfigTimer = setTimeout(async () => {
		const payload = {
			botMode: hostSettings.botMode,
			localModel: hostSettings.localModel,
			localBotCount: hostSettings.localBotCount
		};
		try {
			await fetch('/gameState', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});
		} catch {
			/* ignore network hiccups */
		}
	}, 150);
}

function renderHostPanel(force = false) {
	const container = document.getElementById("host_panel");
	if (!container || !gameState) return;
	const signature = JSON.stringify({
		isHost: gameState.isHost,
		mode: hostSettings.botMode,
		model: hostSettings.localModel,
		count: hostSettings.localBotCount,
		options: modelOptions.map(opt => opt.id),
	});
	if (!force && container.dataset.signature === signature) return;
	container.dataset.signature = signature;

	const status = gameState.botStatus || {};
	if (!gameState.isHost) {
		const selected = modelOptions.find(opt => opt.id === gameState.localModel);
		container.innerHTML = `
			<div class="host-config">
				<p class="host-note">Waiting for host to start the round…</p>
				<p>Mode: ${gameState.botMode === "local_ai" ? "Local AI agents" : "Cloud API bots"}</p>
				${selected ? `<p>Model: ${selected.label}</p>` : ""}
				<p class="host-model-hint">Local bots running: ${status.running || 0}</p>
			</div>
		`;
		return;
	}

	const optionsHtml = modelOptions.map(opt => `
		<option value="${opt.id}" ${opt.id === hostSettings.localModel ? "selected" : ""}>
			${opt.label}
		</option>
	`).join("") || `<option>No models found</option>`;

	const selected = modelOptions.find(opt => opt.id === hostSettings.localModel);
	const localSectionClass = hostSettings.botMode === "local_ai" ? "host-local" : "host-local hidden";
	const desc = selected ? `${selected.description} <br> <strong>${selected.hardware}</strong>` : "Configure models in bot_profiles.py.";

	container.innerHTML = `
		<div class="host-config">
			<h3>Match Setup</h3>
			<label class="host-radio">
				<input type="radio" name="host_bot_mode" value="cloud_api" ${hostSettings.botMode !== "local_ai" ? "checked" : ""}>
				<span>Cloud API bots (existing behavior)</span>
			</label>
			<label class="host-radio">
				<input type="radio" name="host_bot_mode" value="local_ai" ${hostSettings.botMode === "local_ai" ? "checked" : ""}>
				<span>Local AI agents</span>
			</label>
			<div class="${localSectionClass}">
				<label>
					Local model
					<select id="local_model_select">
						${optionsHtml}
					</select>
				</label>
				<label>
					Number of local bots (1-6)
					<input id="local_bot_count" type="number" min="1" max="6" value="${hostSettings.localBotCount}">
				</label>
				<div class="host-model-hint">${desc}</div>
			</div>
			<p class="host-model-hint">
				Local bots requested: ${hostSettings.localBotCount} • Active: ${status.running || 0}
			</p>
		</div>
	`;

	const modeInputs = container.querySelectorAll('input[name="host_bot_mode"]');
	modeInputs.forEach(input => {
		input.addEventListener('change', () => {
			hostSettings.botMode = input.value;
			renderHostPanel(true);
			persistHostSettings();
		});
	});

	const modelSelect = container.querySelector('#local_model_select');
	if (modelSelect) {
		modelSelect.addEventListener('change', () => {
			hostSettings.localModel = modelSelect.value;
			renderHostPanel(true);
			persistHostSettings();
		});
	}

	const countInput = container.querySelector('#local_bot_count');
	if (countInput) {
		countInput.addEventListener('change', () => {
			const parsed = parseInt(countInput.value, 10);
			if (!Number.isNaN(parsed)) {
				hostSettings.localBotCount = Math.min(6, Math.max(1, parsed));
				countInput.value = hostSettings.localBotCount;
				renderHostPanel(true);
				persistHostSettings();
			}
		});
	}
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
			if (!gameState) return;
			const payload = {
				nextPhase: true
			};
			if (gameState.isHost) {
				payload.botMode = hostSettings.botMode;
				payload.localModel = hostSettings.localModel;
				payload.localBotCount = hostSettings.localBotCount;
			}
			fetch('/gameState', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});
		});
		startButton.dataset.listenerAdded = "True";
	}
	if (startButton) {
		startButton.disabled = !gameState.isHost;
		startButton.title = gameState.isHost ? "" : "Waiting for host";
	}
	renderHostPanel();
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
			if (!gameState) return;
			const payload = {
				nextPhase: true
			};
			if (gameState.isHost) {
				payload.botMode = hostSettings.botMode;
				payload.localModel = hostSettings.localModel;
				payload.localBotCount = hostSettings.localBotCount;
			}
			fetch('/gameState', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});
		});
		startButton.dataset.listenerAdded = "True";
	}
	if (startButton) {
		startButton.disabled = !gameState.isHost;
		startButton.title = gameState.isHost ? "" : "Waiting for host";
	}
	renderHostPanel();
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
	const votesById = {};
	players.forEach(p => votesById[p.user_id] = p.votes);
	const maxVotes = players.length > 0 ? Math.max(...players.map(p => p.votes)) : 0;
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


