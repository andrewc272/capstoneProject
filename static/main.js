let gameState;
let realized_gameState;
let game_HTML;
let users;
let form_shown = false;


async function update_gameState(){
	// updates the game state on client side
	try {
		const response = await fetch('/gameState');

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		gameState = await response.json();
		users = gameState.users;
	} catch (error) {
		console.error('Error fetching data:', error);
		return;
	}
}

async function update_gameFrame(){
	//renders HTML for each of the phases of the game
	try {
		const response = await fetch(`/static/${gameState.gamePhase}.html`);
		game_HTML = await response.text();
		realized_gameState = gameState.gamePhase;
		document.getElementById("game").innerHTML = game_HTML;
	} catch(error) {
		console.error('Error fetching html file:', error);
	}

}

async function introJS(){
	//if the game is at the lobby stage create a event listener for it to start the game
	const joinButton = document.getElementById("join_game"); 
	if (joinButton && !joinButton.dataset.listenerAdded) {
		joinButton.addEventListener('click', function() {	
			users = gameState.users;
			fetch('/gameState', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ nextPhase: true })
			})
			.then(res => res.json())
			.then(data => console.log("POST response:", data));
		});
		joinButton.dataset.listenerAdded = "True";


	}
	const myId = gameState.myId;
	document.getElementById("lobby_list").innerHTML = `
  		${gameState.users.map((user, index) => {
    		const isSelf = user === myId;
    		const playerId = isSelf ? 'player-self' : `player${index + 1}`;
    		const playerClass = isSelf ? 'self-player' : 'other-player';
    		const playerLabel = isSelf ? 'You are here!!' : `Player ${index + 1} is here!!`;

    		return `<li id="${playerId}" class="${playerClass}">${playerLabel}</li>`;
  		}).join('')}
	`;

}


async function lobbyJS(){
	//if the game is at the lobby stage create a event listener for it to start the game
	const startButton = document.getElementById("start_game"); 
	if (startButton && !startButton.dataset.listenerAdded) {
		startButton.addEventListener('click', function() {	
			users = gameState.users;
			fetch('/gameState', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ nextPhase: true })
			})
			.then(res => res.json())
			.then(data => console.log("POST response:", data));
		});
		startButton.dataset.listenerAdded = "True";
	}

	const myId = gameState.myId;
	document.getElementById("lobby_list").innerHTML = `
  		${gameState.users.map((user, index) => {
    		const isSelf = user === myId;
    		const playerId = isSelf ? 'player-self' : `player${index + 1}`;
    		const playerClass = isSelf ? 'self-player' : 'other-player';
    		const playerLabel = isSelf ? 'You are here!!' : `Player ${index + 1} is here!!`;

    		return `<li id="${playerId}" class="${playerClass}">${playerLabel}</li>`;
  		}).join('')}
	`;

}

async function chatJS(){
	// generates the chats on the screen
	// TODO make the messaging more seemless by adding JS to fetch and send a POST to flask
	
	const myId = gameState.myId;
	document.getElementById('chat_area').innerHTML = `
		<ul>
			${gameState.chats.map(chat => {
			const isSelf = chat[0] === myId;
			const playerId = isSelf ? 'self-player' : `player${users.indexOf(chat[0]) + 1}`;
			const playerClass = isSelf ? 'self-player' : 'other-player';

			return `<li id="player${users.indexOf(chat[0]) + 1}" class="${playerClass}">${chat[1]}</li>`
			}).join('')}
		</ul>
	`;

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
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(data)
			})
			.then(res => res.json())
			.then(data => console.log("POST response:", data));
		});
		form.dataset.listenerAdded = "True";
	}
}


async function guessJS(){

	const form = document.getElementById("submit_button");
	if (submitButton && !submitButton.dataset.listenerAdded) {
		submitButton.addEventListener('click', function() {	
			fetch('/gameState', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ nextPhase: true })
			})
			.then(res => res.json())
			.then(data => console.log("POST response:", data));
		});
		submitButton.dataset.listenerAdded = "True";
	}

	if( !form_shown ){
		const myId = gameState.myId;

		document.getElementById("lobby_list").innerHTML = `
  			${gameState.users.map((user, index) => {
    			const isSelf = user === myId;
    			const playerId = isSelf ? 'player-self' : `player${index + 1}`;
    			const playerClass = isSelf ? 'self-player' : 'other-player';
    			const playerLabel = isSelf ? 'Yourself' : `Player ${index + 1}`;

    			return `<label><input type="checkbox" name="element" value="${playerId}">${playerLabel}</label>`;
  			}).join('')}
		`;
			form_shown = true;
	}
}

async function updateGame(){
	update_gameState();

	if (gameState.gamePhase != realized_gameState ){
		update_gameFrame();
	}

	//implements JS for each of the phases of the game
	if (gameState.gamePhase == "intro"){
		introJS();
	}
	else if (gameState.gamePhase == "lobby"){
		lobbyJS();
	}
	else if (gameState.gamePhase == "chat"){
		chatJS();
	}
	else if (gameState.gamePhase == "guess"){
		guessJS();
	}
}


//TODO make an async request that won't return until there is a change to the state of the game this will prevent issues that could arise 
setInterval(updateGame, 500);
