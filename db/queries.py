import psycopg
from psycopg.rows import dict_row
from psycopg import sql

async def get_player_search_info():
    async with await psycopg.AsyncConnection.connect("dbname=nfl user=mac") as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("""
                            SELECT
                                p.id AS player_id, p.firstname, p.lastname, p.position,
                                p.firstname || ' ' || p.lastname AS full_name,
                                t.name AS team_abbrev
                            FROM players AS p
                            JOIN teams AS t on p.team_id = t.id;
                            """)
            players = await cur.fetchall()
            return players


async def get_teamate_correlation_info(player_id):
    async with await psycopg.AsyncConnection.connect("dbname=nfl user=mac") as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("""
                              SELECT team_id FROM players WHERE id = %s;
                            """, (player_id,))
            result = await cur.fetchone()
            team_id = result["team_id"]

            await cur.execute("""
                            SELECT
                            p.id AS player_id,
                            p.firstname,
                            p.lastname,
                            p.firstname || ' ' || p.lastname AS full_name,
                            p.position,
                            t.name AS team_abbrev
                        FROM players AS p
                        JOIN teams AS t ON p.team_id = t.id
                        WHERE p.team_id = %s;
                    """, (team_id, ))
            players = await cur.fetchall()
            if not players:
                return [], []
            
            ids = [p["player_id"]for p in players]

            gamelog_query = ("""
                              SELECT * FROM player_gamelogs WHERE player_id = ANY(%s);
                            """)
            await cur.execute(gamelog_query, [ids])
            gamelogs = await cur.fetchall()

            return players, gamelogs

async def get_player(player_id):
    async with await psycopg.AsyncConnection.connect("dbname=nfl user=mac") as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("""
                               SELECT
                                p.id AS player_id, p.firstname, p.lastname, p.position,
                                p.firstname || ' ' || p.lastname AS full_name,
                                t.name AS team_abbrev
                            FROM players AS p
                            JOIN teams AS t on p.team_id = t.id
                            WHERE p.id = %s;
                        """, (player_id, ))
            player = await cur.fetchone()
            if not player:
                return None
            return player

    


