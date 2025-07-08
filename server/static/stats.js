//I want the user at some point to be able to edit the range of games for this average so were doing it with JS

document.addEventListener('DOMContentLoaded', () => {
    const playerData = window.TEAM_PLAYER_DATA;
    const gamelogs = window.TEAM_GAMELOGS;
    const searchedPlayer = window.SEARCHED_PLAYER;

    const titleRow = document.querySelector('.correlation-table .title-row');
    const playerCard = document.querySelector('.player-card');
    const playerMap = new Map(playerData.map(player => [player.player_id, player]));
    
    for (let i = 0; i < playerData.length; i++) {
        playerData[i]["dk_games"] = [];
        playerData[i]["fd_games"] = [];
    }
    console.log(gamelogs)    
    for (let i = 0; i < gamelogs.length; i++) {
        const foundPlayer = playerMap.get(gamelogs[i]["player_id"]);

        
        if (foundPlayer && gamelogs[i]["dnp"] != true) {
            foundPlayer.dk_games.push(gamelogs[i]["draftkings_pts"]);
            foundPlayer.fd_games.push(gamelogs[i]["fanduel_pts"]);
        } 


    }

    for (let i = 0; i < playerData.length; i++) {
        const dk_sum = playerData[i]["dk_games"].reduce((curSum, curVal) => curSum + curVal, 0);
        playerData[i]["avg_dk_points"] = dk_sum / playerData[i]["dk_games"].length;

        const fd_sum = playerData[i]["fd_games"].reduce((curSum, curVal) => curSum + curVal, 0);
        playerData[i]["avg_fd_points"] = fd_sum / playerData[i]["fd_games"].length;
    }

   
    const dkCorHeader = titleRow.querySelector('th:nth-child(2)');

    const dkAvgHeader = document.createElement('th');
    dkAvgHeader.textContent = 'DK Average Fpts';

    const fdAvgHeader = document.createElement('th');
    fdAvgHeader.textContent = 'FD Average Fpts';
    
    titleRow.insertBefore(fdAvgHeader, dkCorHeader);
    titleRow.insertBefore(dkAvgHeader, fdAvgHeader);
    
    //player rows

    const playerRows = document.querySelectorAll('.correlation-table tbody tr')

    playerRows.forEach(row => {
        const playerId = parseInt(row.dataset.playerId); // Get player_id from data attribute
        const player = playerMap.get(playerId);

        if (player) {
            const playerNameCell = row.querySelector('td:first-child');
            const dkAvgCell = document.createElement('td');
            dkAvgCell.textContent = player.avg_dk_points.toFixed(2);

            const fdAvgCell = document.createElement('td');
            fdAvgCell.textContent = player.avg_fd_points.toFixed(2);

            row.insertBefore(fdAvgCell, playerNameCell.nextElementSibling);
            row.insertBefore(dkAvgCell, playerNameCell.nextElementSibling.nextElementSibling);
        } else {
            console.warn(`HTML row for player ID ${playerId} found, but player data not in JS array.`);
        }
    });

    //This is not stats but it makes sense to put this here
    if (searchedPlayer && playerCard) {
        const teamLogo = document.createElement('img');
        const team = searchedPlayer.team_abbrev;

        logoSrc = `/static/images/${team}.svg`;
        teamLogo.src = logoSrc;
        teamLogo.alt = `${team} logo`;
        teamLogo.classList.add('team-logo');

        playerCard.prepend(teamLogo);
    } else {
        console.error("Could not display team logo: PlayerCard or searchedPlayer missing");
    }


});
