from typing import Union
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from db import queries
from sb_math import stats

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def main_search(request: Request):
    try:
        all_players = await queries.get_player_search_info()
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "players": all_players}
        )

    except Exception as e:
        print(f"Error fetching players for autocomplete: {e}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Could not load player data for search. Please try again later."},
            status_code=500
        )

@app.get("/player_search_results", response_class=HTMLResponse)
async def player_search_results(request: Request, player_id: int):
    try: 
        players, gamelogs = await queries.get_teamate_correlation_info(player_id)
        players, gamelogs = stats.player_correlation(player_id, players, gamelogs)
        searched_player = await queries.get_player(player_id)

        return templates.TemplateResponse("results.html",
                                          {"request": request, "searched_id": player_id,"searched_player": searched_player, "players": players, "gamelogs": gamelogs})
    except Exception as e:
        print(f"Error fetching players for autocomplete: {e}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Could not load player data for search. Please try again later."},
            status_code=500
        )

@app.get("/math", response_class=HTMLResponse)
async def return_math(request: Request):
    return templates.TemplateResponse("math.html", {"request": request})



@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


