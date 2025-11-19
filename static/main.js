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

async function introJS() {
	// If the game is at the intro stage, add an event listener to the Join Game button
	const joinButton = document.getElementById("join_game");
	if (joinButton && !joinButton.dataset.listenerAdded) {
		joinButton.addEventListener('click', async function() {
			try {
				// Step 1: Tell the backend this player is joining
				const joinResponse = await fetch('/addPlayer');
				const joinData = await joinResponse.json();
				console.log("Player joined:", joinData);

				// Step 2: Then move from 'intro' → 'lobby' (but do NOT start the game yet)
				//const phaseResponse = await fetch('/gameState', {
					//method: 'POST',
					//headers: { 'Content-Type': 'application/json' },
					//body: JSON.stringify({ nextPhase: true })
				//});
				//const phaseData = await phaseResponse.json();
				//console.log("Phase advanced:", phaseData);

			} catch (error) {
				console.error("Error joining game:", error);
			}
		});

		joinButton.dataset.listenerAdded = "True";
	}

    //stolen from lobbyJS
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


	// Display the current list of players in the lobby
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


async function guessJS() {
    const myId = gameState.myId;
    const users = gameState.users;

    // creating player list with buttons
    if (!form_shown) {
        const lobbyDiv = document.getElementById("lobby_list");

        lobbyDiv.innerHTML = `
            ${users.map((userId, index) => {
                const isSelf = userId === myId;
                const labelName = isSelf ? "You" : `Player ${index + 1}`;

                // Use the real userId in the "name" so we can map it back on submit
                const fieldName = `vote-${userId}`;

                return `
                    <div class="player-row">
                        <span class="player-name">${labelName}</span>

                        <label>
                            <input type="radio"
                                   name="${fieldName}"
                                   value="human"
                                   required>
                            Human
                        </label>

                        <label>
                            <input type="radio"
                                   name="${fieldName}"
                                   value="ai">
                            AI
                        </label>
                    </div>
                `;
            }).join('')}
        `;

        form_shown = true;
    }

    // 2) Attach a submit handler to the form (once)
    const form = document.getElementById("guess_form");
    if (form && !form.dataset.listenerAdded) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            const formData = new FormData(form);

            // Build an array of { target: <user_id>, guess: "human" | "ai" }
            const votes = users.map((userId) => {
                const fieldName = `vote-${userId}`;
                const guess = formData.get(fieldName);  // "human" or "ai"
                return { target: userId, guess: guess };
            });

			// Send votes to backend
			await fetch("/vote", {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({ votes })
			});

			Array.from(form.elements).forEach(el => el.disabled = true);

    		console.log("Votes submitted");
        });
	
        form.dataset.listenerAdded = "True";
    }
}


async function resultsJS() {
    const myId = gameState.myId;
    const users = gameState.users;      // list of user_ids in turn order / join order
    const players = gameState.players;  // [{ user_id, votes }, ...]

    const container = document.getElementById("results_container");
    if (!container) return;

    // Build a quick lookup: user_id -> votes
    const votesById = {};
    players.forEach(p => {
        votesById[p.user_id] = p.votes;
    });

	const maxVotes = players.length > 0
        ? Math.max(...players.map(p => p.votes))
        : 0;

    // Build HTML rows in the same order as `users`
    container.innerHTML = `
        <ul class="results-list">
            ${users.map((userId, index) => {
                const isSelf = userId === myId;
                const displayName = isSelf ? "You" : `Player ${index + 1}`;
                const votes = votesById[userId] ?? 0;

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
	else if (gameState.gamePhase == "results"){
		resultsJS();
	}
}


//TODO make an async request that won't return until there is a change to the state of the game this will prevent issues that could arise 
setInterval(updateGame, 500);
