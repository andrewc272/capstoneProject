let gameState;
let chats = ['Apple', 'Banana', 'Oranges']
let realized_gameState;
let game_HTML

async function updateGame(){
	// first update gameState
	try {
		const response = await fetch('/gameState');

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		gameState = await response.json();
	} catch (error) {
		console.error('Error fetching data:', error);
		return;
	}

	// now update the HTML to show what game phase the room is in
	if (gameState.gamePhase != realized_gameState ){
		try {
			const response = await fetch(`/static/${gameState.gamePhase}.html`);
			game_HTML = await response.text();
			realized_gameState = gameState.gamePhase;
			document.getElementById("game").innerHTML = game_HTML;
		} catch(error) {
			console.error('Error fetching html file:', error);
		}
	}

	//if the game is at the lobby stage create a event listener for it to start the game
	if (gameState.gamePhase == "lobby"){
	// TODO check if there is already an event listener so that there isn't more added
		const startButton = document.getElementById("start_game"); 
		if (startButton && !startButton.dataset.listenerAdded) {
			startButton.addEventListener('click', function() {	
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
	}
	// if the game si at the chat stage the <ul> should be filled with the chats <li>
	// TODO: load chats from server side
	else if (gameState.gamePhase == "chat"){
	// generates the chats
	// TODO move this function so that it can be called and updated seperately and quicker	
		document.getElementById('chat_area').innerHTML = `
			<ul>
				${gameState.chats.map(chat => `<li>${chat}</li>`).join('')}
			</ul>
			`;
		}
}



setInterval(updateGame, 1000);
