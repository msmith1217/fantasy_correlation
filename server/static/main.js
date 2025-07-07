// static/main.js

function debounce(func, delay) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), delay);
    };
}

document.addEventListener('DOMContentLoaded', () => {

    const playerSearchInput = document.getElementById('playerSearch'); // The text input box
    const playerSuggestionsDatalist = document.getElementById('playerSuggestions'); // The hidden list for suggestions
    const selectedPlayerIdInput = document.getElementById('selectedPlayerId'); // The hidden input to store player ID
    const searchForm = document.getElementById('searchForm'); 
    
    const playerData = window.ALL_PLAYER_DATA;

    const populateDatalist = (searchTerm) => {
    
        playerSuggestionsDatalist.innerHTML = '';

        const filteredPlayers = playerData.filter(player =>
        (player.full_name && player.full_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (player.team_abbrev && player.team_abbrev.toLowerCase().includes(searchTerm.toLowerCase()))).slice(0, 20);   

        filteredPlayers.forEach(player => {

            const option = document.createElement('option');

            option.value = `${player.full_name}${player.team_abbrev ? ' (' + player.team_abbrev + ')' : ''}`;
            option.setAttribute('data-player-id', player.player_id);
            playerSuggestionsDatalist.appendChild(option);
        });
    };
    
    playerSearchInput.addEventListener('input', debounce((event) => {
    const searchTerm = event.target.value;
    populateDatalist(searchTerm);
    }, 300));

    searchForm.addEventListener('submit', (event) => { 
        event.preventDefault();

        const enteredName = playerSearchInput.value;
        let foundPlayer = null;

        foundPlayer = playerData.find(player => {
            if (player.full_name && player.full_name.toLowerCase() === enteredName.toLowerCase()) {
                return true;
            }
            const formattedName = `${player.full_name}${player.team_abbrev ? ' (' + player.team_abbrev + ')' : ''}`;
            if (formattedName.toLowerCase() === enteredName.toLowerCase()) {
                return true;
            }
            return false;
        });

        if (!foundPlayer) {
        const options = playerSuggestionsDatalist.options;
            for (let i = 0; i < options.length; i++) {
                if (options[i].value.toLowerCase() === enteredName.toLowerCase()) {
                    const playerId = options[i].getAttribute('data-player-id');
                    if (playerId) {
                        foundPlayer = { player_id: parseInt(playerId) };
                        break;
                    }
                }
            }
            if (options.length > 0) {
                playerId = options[0].getAttribute('data-player-id');
                foundPlayer = { player_id: parseInt(playerId) };
            }
        }

        if (foundPlayer) {
            selectedPlayerIdInput.value = foundPlayer.player_id;
            console.log("found");
            searchForm.submit();
        } else {    
            alert("Please select a valid NFL player from the suggestions or type a full valid name.");
            playerSearchInput.focus();
        } 
    });

});
  
