import json
import requests 
from bs4 import BeautifulSoup
import re
import psycopg
import data_types


adp_url = "https://www.rotowire.com/football/tables/adp.php?pos=ALL&scoring=PPR"

def main():
    rankings = requests.get(adp_url)
    ranking_data = rankings.json()
    supported_pos = ["QB", "RB", "FB", "WR", "TE"]
    done = 433
    for player in ranking_data:
        player_table = {
                "firstname": player["firstname"],
                "lastname": player["lastname"],
                "team": player["team"],
                "position": player["position"],
                "injury": player["injury"]
        }

        if player_table["position"] not in supported_pos:
            continue
        if player["rank"] < done:
            continue
        if player["rank"] > 635:
            break
    
        split_url = player["player"].split('"')
        player_template_url = "https://www.rotowire.com" + split_url[1] 

        player_template = requests.get(player_template_url)
        html_content = player_template.text
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tag = soup.find('script', string=re.compile(r'\$\.ajax'))
    
        if script_tag:
            script_list = re.split(r'[{}]+', str(script_tag))
            useful_part = script_list[2] + "'y data nested'," + script_list[3]
            #some regex nonsense
            json_ready_step1 = re.sub(r"'([^']+)'", r'"\1"', useful_part)
            json_ready_step2 = re.sub(r'(\w+)\s*:', r'"\1":', json_ready_step1)
            json_ready_step3 = "{" + json_ready_step2 + "}"
            json_ready_step4 = re.sub(r',\s*([}\]])', r'\1', json_ready_step3)
            data = json.loads(json_ready_step4)

            #the data i actually wanted
            player_url = f"https://www.rotowire.com{data["url"]}?id={data["id"]}&pos={data["pos"]}&team={data["team"]}&opp={data["opp"]}"
            player_table["gamelog_url"] = player_url
            player_table["id"] = data["id"]
            player_data = requests.get(player_url)
            player_json = player_data.json()
            player_snake = convert_keys_to_snake_case(player_json)
            print(f"Adding {player_table['firstname']} {player_table['lastname']}, player_id: {data['id']}, rank: {player['rank']}")
            insert_magic(player_table, "players", data["id"])
            for i in range(len(player_snake["advanced"]["body"])):
                insert_magic(player_snake["advanced"]["body"][i], "player_season_advanced_stats", data["id"])
            for i in range(len(player_snake["basic"]["body"])):
                insert_magic(player_snake["basic"]["body"][i], "player_season_basic_stats", data["id"])
            for i in range(len(player_snake["fantasy_rz"]["body"])):
                insert_magic(player_snake["fantasy_rz"]["body"][i], "player_season_fantasy_rz_stats", data["id"])
            for i in range(len(player_snake["gamelog"]["body"])):
                if player_snake["gamelog"]["body"][i]["week"] == player_snake["gamelog"]["body"][i-1]["week"] and  player_snake["gamelog"]["body"][i]["dnp"] == True:
                    pass
                insert_magic(player_snake["gamelog"]["body"][i], "player_gamelogs", data["id"])
            if player_table["position"] != "QB":
                for i in range(len(player_snake["alignment"]["detailed"])):
                    insert_magic(player_snake["alignment"]["detailed"][i], "player_alignment_stats", data["id"])
            for i in range(len(player_snake["splits"]["body"])):
                insert_magic(player_snake["splits"]["body"][i], "player_season_splits", data["id"])
            
        
            #print(player_json)
   



def insert_magic(json_dict, table, player_id):
    with psycopg.connect("dbname=nfl user=mac") as conn:
        with conn.cursor() as cur:
            if table != "players":
                json_dict["player_id"] = player_id
            if "team" in json_dict:
                json_dict["team_id"] = data_types.team_id_lookup[json_dict["team"]]
                del json_dict["team"]
            season_check = table + "." + "season"
            if "season" not in json_dict and season_check in data_types.db:
                json_dict["season"] = "2024"
            columns, placeholders, values = "", "", []
            for key, value in json_dict.items():
                columns = columns + key + ", "
                placeholders = placeholders + "%s, "
                mod_key = table + "." + key
                c_type = data_types.db[mod_key]
                fixed_val = None
                if c_type == "NUMERIC":
                    fixed_val = convert_to_numeric(value)
                elif c_type == "INTEGER":
                    fixed_val = convert_to_integer(value)
                else:
                    fixed_val = value

                values.append(fixed_val)
            columns = columns[0:-2]
            placeholders = placeholders[0:-2]
            insert = f" INSERT INTO {table} ({columns}) VALUES ({placeholders});"
            try:
                cur.execute(insert, values)
                conn.commit()
            except psycopg.Error as e:
                print(f"Database error: {e}")
                print(insert)
                print(values)
                if conn:
                    conn.rollback() # Rollback in case of error
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            finally:
                if conn:
                    cur.close()
                    conn.close()
                    #print(f"New {table} entry")

def camel_to_snake(name):
    # 1. Insert an underscore between a lowercase letter and an uppercase letter.
    #    This handles cases like "fptsHalf" -> "fpts_Half".
    name = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', name)

    # 2. Insert an underscore between an uppercase letter and another uppercase letter
    #    IF the second uppercase letter is followed by a lowercase letter.
    #    This handles acronyms correctly, e.g., "rushTDPct" -> "rush_TDPct"
    #    (The 'TD' stays together, and then it puts an underscore before 'P')
    name = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', '_', name)

    return name.lower()

def convert_keys_to_snake_case(obj):
    if isinstance(obj, dict):
        return {camel_to_snake(k): convert_keys_to_snake_case(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys_to_snake_case(elem) for elem in obj]
    else:
        return obj
            
def convert_to_numeric(value):
    """
    Converts a string value to a float for NUMERIC columns.
    Handles '-' and empty strings by returning None (NULL in SQL).
    """
    if value is None or str(value).strip() == '-' or str(value).strip() == '':
        return None
    try:
        return float(value)
    except ValueError:
        return None # Or raise an error if invalid data should halt the process

def convert_to_integer(value):
    """
    Converts a string value to an integer.
    Handles '-' and empty strings by returning None (NULL in SQL).
    """
    if value is None or str(value).strip() == '-' or str(value).strip() == '':
        return None
    try:
        return int(float(value)) # Convert to float first to handle '0.0' or similar
    except ValueError:
        return None
if __name__ == '__main__':
    main()
