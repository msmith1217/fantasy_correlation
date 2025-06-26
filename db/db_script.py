import re

def parse_sql_schema(sql_ddl):
    """
    Parses SQL CREATE TABLE statements to extract column names and their types.

    Args:
        sql_ddl (str): A string containing one or more CREATE TABLE statements.

    Returns:
        dict: A dictionary where keys are 'table.column' and values are their types.
              Types are simplified (e.g., 'VARCHAR(5)' becomes 'VARCHAR', 'NUMERIC(5,2)' becomes 'NUMERIC').
    """
    column_data = {}

    # Split the DDL into individual CREATE TABLE statements
    # This regex handles CREATE TABLE IF NOT EXISTS and similar variations
    table_statements = re.findall(r'CREATE TABLE(?: IF NOT EXISTS)?\s+(\w+)\s*\((.*?)\);', sql_ddl, re.DOTALL | re.IGNORECASE)

    for table_name, columns_str in table_statements:
        table_name = table_name.lower() # Convert table name to lowercase for consistency

        # Split columns string by comma, being careful not to split inside parentheses (e.g., for NUMERIC(5,2))
        # This regex splits by comma that is NOT inside parentheses.
        columns = re.split(r',\s*(?![^()]*\))', columns_str.strip())

        for col_def in columns:
            col_def = col_def.strip()
            if not col_def:
                continue

            # Skip lines that are likely PRIMARY KEY or FOREIGN KEY constraints directly
            if col_def.lower().startswith(('primary key', 'foreign key')):
                continue

            # Regex to find column name and its type
            # It captures the first word as the column name and the next word (or pattern) as the type
            match = re.match(r'(\w+)\s+([A-Z_]+(?:\(\d+(?:,\d+)?\))?(?:\s+\w+)*)', col_def, re.IGNORECASE)
            if match:
                column_name = match.group(1).lower()
                column_type_raw = match.group(2).upper()

                # Simplify the type: remove precision/scale for NUMERIC/VARCHAR etc.
                # And remove other modifiers like 'NOT NULL', 'PRIMARY KEY', 'SERIAL', 'TEXT' etc.
                simple_type_match = re.match(r'([A-Z_]+)(?:\(\d+(?:,\d+)?\))?', column_type_raw)
                if simple_type_match:
                    simple_type = simple_type_match.group(1)
                else:
                    # Fallback for types like TEXT, BOOLEAN, etc.
                    simple_type_parts = column_type_raw.split()
                    simple_type = simple_type_parts[0]

                # Special handling for SERIAL, as it's typically an INTEGER type
                if simple_type == 'SERIAL':
                    simple_type = 'INTEGER'
                elif simple_type == 'TEXT': # TEXT is a specific type in PostgreSQL
                    simple_type = 'TEXT'
                elif simple_type == 'BOOLEAN': # BOOLEAN is a specific type
                    simple_type = 'BOOLEAN'
                elif 'VARCHAR' in simple_type: # Ensure VARCHAR comes out as VARCHAR
                    simple_type = 'VARCHAR'
                elif 'NUMERIC' in simple_type: # Ensure NUMERIC comes out as NUMERIC
                    simple_type = 'NUMERIC'
                elif 'INTEGER' in simple_type: # Ensure INTEGER comes out as INTEGER
                    simple_type = 'INTEGER'


                key = f"{table_name}.{column_name}"
                column_data[key] = simple_type

    return column_data

# Your provided SQL DDL
sql_schema = """
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(5) NOT NULL);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    firstname VARCHAR(32),
    lastname VARCHAR(32),
    team_id INTEGER,
    position VARCHAR(5),
    injury VARCHAR(255),
    gamelog_url TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id));

CREATE TABLE IF NOT EXISTS player_season_advanced_stats (
    player_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    games INTEGER,
    broken_tackles INTEGER,
    broken_tackle_pct NUMERIC(5,2),
    pos_run_pct NUMERIC(5,2),
    inside_run_pct NUMERIC(5,2),
    outside_run_pct NUMERIC(5,2),
    rush_td_pct NUMERIC(5,2),
    rush_yac INTEGER,
    avg_rush_yac NUMERIC(5,2),
    rush_yac_pct NUMERIC(5,2),
    air_yards INTEGER,
    completed_air_yards INTEGER,
    ay_snap NUMERIC(5,2),
    yac INTEGER,
    avg_yac NUMERIC(5,2),
    rec_yac_pct NUMERIC(5,2),
    avg_completed_air_yards NUMERIC(5,2),
    a_dot NUMERIC(5,2),
    catch_rate NUMERIC(5,2),
    drop_rate NUMERIC(5,2),
    air_yard_share NUMERIC(5,2),
    target_share NUMERIC(5,2),
    drawn_pi INTEGER,
    offensive_pi INTEGER,
    yards_pi INTEGER,
    yards_lost_to_penalties INTEGER,
    routes INTEGER,
    tprr NUMERIC(5,2),
    yprr NUMERIC(5,2),
    PRIMARY KEY (player_id, season, team_id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS player_season_basic_stats (
    player_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    age INTEGER,
    games INTEGER,
    snaps_off INTEGER,
    snaps_def INTEGER,
    snaps_special INTEGER,
    fumbles_off INTEGER,
    fumbles_lost INTEGER,
    rush_att INTEGER,
    rush_yds INTEGER,
    rush_td INTEGER,
    rush_avg NUMERIC(5,2),
    rush20 INTEGER,
    rush40 INTEGER,
    rush100 INTEGER,
    rush150 INTEGER,
    rush200 INTEGER,
    rec INTEGER,
    rec_yds INTEGER,
    rec_td INTEGER,
    rec_avg NUMERIC(5,2),
    rec20 INTEGER,
    rec40 INTEGER,
    rec100 INTEGER,
    rec150 INTEGER,
    rec200 INTEGER,
    targets INTEGER,
    yds_target NUMERIC(5,2),
    drops INTEGER,
    kick_ret_yds INTEGER,
    kick_ret_td INTEGER,
    punt_ret_yds INTEGER,
    punt_ret_td INTEGER,
    PRIMARY KEY (player_id, season, team_id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS player_season_fantasy_rz_stats (
    player_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    age INTEGER,
    games INTEGER,
    standard NUMERIC(5,2),
    halfppr NUMERIC(5,2),
    ppr NUMERIC(5,2),
    rz_touches_team_pct NUMERIC(5,2),
    rz_touches20 INTEGER,
    rz_touches10 INTEGER,
    rz_touches5 INTEGER,
    rz_touches20_conv NUMERIC(5,2),
    rz_touches10_conv NUMERIC(5,2),
    rz_touches5_conv NUMERIC(5,2),
    rz_rec_team_pct NUMERIC(5,2),
    rz_rec20 INTEGER,
    rz_rec10 INTEGER,
    rz_rec5 INTEGER,
    rz_rec20_conv NUMERIC(5,2),
    rz_rec10_conv NUMERIC(5,2),
    rz_rec5_conv NUMERIC(5,2),
    rz_rush_team_pct NUMERIC(5,2),
    rz_rush20 INTEGER,
    rz_rush10 INTEGER,
    rz_rush5 INTEGER,
    rz_rush20_conv NUMERIC(5,2),
    rz_rush10_conv NUMERIC(5,2),
    rz_rush5_conv NUMERIC(5,2),
    rec_per_game NUMERIC(5,2),
    rec_yards_per_game NUMERIC(5,2),
    rush_att_per_game NUMERIC(5,2),
    rush_yards_per_game NUMERIC(5,2),
    touches_per_game NUMERIC(5,2),
    yards_per_game NUMERIC(5,2),
    PRIMARY KEY (player_id, season, team_id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS player_gamelogs (
    player_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL, 
    week VARCHAR(10),             -- Can be a number or 'BYE'
    opp VARCHAR(10),    -- Opponent team
    game_url TEXT,
    is_home BOOLEAN,
    dnp BOOLEAN,            
    snaps_off INTEGER,
    snaps_def INTEGER,
    snaps_special INTEGER,
    standard_pts NUMERIC(5,2),
    halfppr_pts NUMERIC(5,2),
    ppr_pts NUMERIC(5,2),
    fanduel_pts NUMERIC(5,2),
    draftkings_pts NUMERIC(5,2),
    yahoo_pts NUMERIC(5,2),
    rec INTEGER,
    rec_yds INTEGER,
    rec_td INTEGER,
    rec_avg NUMERIC(5,2),
    rec20 INTEGER,
    rec40 INTEGER,
    targets INTEGER,
    yds_target NUMERIC(5,2),
    routes INTEGER,
    tprr NUMERIC(5,2),
    yprr NUMERIC(5,2),
    rush_att INTEGER,
    rush_yds INTEGER,
    rush_td INTEGER,
    rush_avg NUMERIC(5,2),
    rush20 INTEGER,
    rush40 INTEGER,
    fumbles_off INTEGER,
    fumbles_lost INTEGER,
    rz_pass20 INTEGER,
    rz_pass10 INTEGER,
    rz_pass5 INTEGER,
    rz_rush20 INTEGER,
    rz_rush10 INTEGER,
    rz_rush5 INTEGER,
    rz_targets20 INTEGER,
    rz_targets10 INTEGER,
    rz_targets5 INTEGER,
    kick_ret_yds INTEGER,
    kick_ret_td INTEGER,
    punt_ret_yds INTEGER,
    punt_ret_td INTEGER,
    standard_def INTEGER,
    halfppr_def INTEGER,
    ppr_def INTEGER,
    fanduel_def INTEGER,
    draftkings_def INTEGER,
    yahoo_def INTEGER,
    PRIMARY KEY (player_id, game_id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS player_alignment_stats (
    player_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    alignment VARCHAR(50) NOT NULL,   -- e.g., 'Left Outside', 'Right Slot'
    plays INTEGER,
    pct NUMERIC(5,2),
    rec INTEGER,
    yards INTEGER,
    td INTEGER,
    yac INTEGER,
    drops INTEGER,
    standard_pp NUMERIC(5,2),
    halfppr_pp NUMERIC(5,2),
    ppr_pp NUMERIC(5,2),
    standard NUMERIC(5,2),
    halfppr NUMERIC(5,2),
    ppr NUMERIC(5,2),
    PRIMARY KEY (player_id, season, alignment),
    FOREIGN KEY (player_id) REFERENCES players(id)
);    


CREATE TABLE IF NOT EXISTS player_season_splits (
    player_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    split_id VARCHAR(50) NOT NULL, -- Unique identifier for the type of split (e.g., 'H', 'A', 'Grass', '1stHalf', 'W')
    split_name VARCHAR(100), -- Descriptive name of the split (e.g., 'Home', 'Away', 'Grass', '1st Half')
    fumbles INTEGER,
    fpts NUMERIC(5,2),
    fpts_half NUMERIC(5,2),
    fpts_ppr NUMERIC(5,2),
    rush_att INTEGER,
    rush_yards INTEGER,
    rush_td INTEGER,
    rush_yac INTEGER,
    broken_tackles INTEGER,
    inside_runs INTEGER,
    outside_runs INTEGER,
    runs_stuffed INTEGER,
    targ INTEGER,
    rec INTEGER,
    rec_td INTEGER,
    rec_yards INTEGER,
    comp_air_yards INTEGER,
    rec_yac INTEGER,
    drops INTEGER,
    a_dot NUMERIC(5,2),
    rec_ypc NUMERIC(5,2),
    PRIMARY KEY (player_id, season, split_id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);
"""

# Generate the dictionary
column_type_dict = parse_sql_schema(sql_schema)

# Print the dictionary
import json
print(json.dumps(column_type_dict, indent=4))
