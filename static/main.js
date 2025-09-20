let gameState;
let chats = ['Apple', 'Banana', 'Oranges']


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
	try {
		const response = await fetch(`/static/${gameState.gamePhase}.html`);
		const html = await response.text();

		document.getElementById("game").innerHTML = html;
		//if the game is at the lobby stage create a event listener for it to start the game
		if (gameState.gamePhase == "lobby"){
			document.getElementById('start_game').addEventListener('click', function() {
				
				fetch('/gameState', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ startGame: true })
				})
				.then(res => res.json())
				.then(data => console.log("POST response:", data));
			});
		}
		// if the game si at the chat stage the <ul> should be filled with the chats <li>
		// TODO: load chats from server side
		else if (gameState.gamePhase == "chat"){
			document.getElementById('chat_area').innerHTML = `
				<ul>
					${chats.map(chat => `<li>${chat}</li>`).join('')}
				</ul>
				`;
		}
	} catch(error) {
		console.error('Error fetching html file:', error);
	}
}



setInterval(updateGame, 1000);
