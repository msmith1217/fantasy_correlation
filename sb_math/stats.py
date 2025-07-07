import numpy as np


def player_correlation(search_player: int, players, gamelogs):
    p1dk, p1fd = {}, {}
    schedule = {}
    w_conv = {"WC":"19", "DIV":"20", "CC":"21", "SB":"22"}
    processed_players = []

    for player in players:
        if player["player_id"] == search_player:
            for log in gamelogs:
                if log["player_id"] ==  search_player and log["draftkings_pts"] != None and log["dnp"] != True:
                    if log["week"] in w_conv:
                        log["week"] = w_conv[log["week"]]

                    p1dk[log["week"]] = log["draftkings_pts"]
                    p1fd[log["week"]] = log["fanduel_pts"]
                    schedule[log["week"]] = log["opp"]

    for player in players:

        if player["player_id"] == search_player:
            continue
        # make dataset
        p2dk, p2fd = {}, {}

        for log in gamelogs:
            if log["player_id"] == player["player_id"] and log["draftkings_pts"] != None and log["dnp"] != True:
                if log["week"] in schedule:
                    if log["opp"] == schedule[log["week"]]:
                        if log["week"] in w_conv:
                            log["week"] = w_conv[log["week"]]
                        p2dk[log["week"]] = log["draftkings_pts"]
                        p2fd[log["week"]] = log["fanduel_pts"]

        pa1dk, pa2dk, pa1fd, pa2fd = [], [], [], []

        for i in range(22):
            week = str(i+1)
            if week in p1dk and week in p2dk:
                pa1dk.append(p1dk[week])
                pa2dk.append(p2dk[week])
                pa1fd.append(p1fd[week])
                pa2fd.append(p2fd[week])


        np1dk = np.array(list(pa1dk), dtype='float32')
        np2dk = np.array(list(pa2dk), dtype='float32')
        np1fd = np.array(list(pa1fd), dtype='float32')
        np2fd = np.array(list(pa2fd), dtype='float32')
  

        dkm = np.corrcoef(np1dk, np2dk)
        fdm = np.corrcoef(np1fd, np2fd)

        player["dk_cor"] = dkm[0, 1]
        player["fd_cor"] = fdm[0, 1]

        if not np.isnan(player['dk_cor']) and not np.isnan(player['fd_cor']):
            processed_players.append(player)

    return processed_players, gamelogs
    

        


    
