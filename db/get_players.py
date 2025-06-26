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

    print(ranking_data[0])
    for player in ranking_data:
    
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
            print(json_ready_step4)
            data = json.loads(json_ready_step4)

            #the data i actually wanted
            player_url = f"https://www.rotowire.com{data["url"]}?id={data["id"]}&pos={data["pos"]}&team={data["team"]}&opp={data["opp"]}"
            player_data = requests.get(player_url)
            player_json = player_data.json()
            insert_magic(player_json["advanced"]["body"][0], "player_season_advanced_stats", data["id"])
        break
            #print(player_json)
   



def insert_magic(json_dict, table, player_id):
    with psycopg.connect("dbname=nfl user=mac") as conn:
        with conn.cursor() as cur:
            json_dict["player_id"] = player_id
            if "team" in json_dict:
                json_dict["team_id"] = data_types.team_id_lookup[json_dict["team"]]
                del json_dict["team"]
            columns, placeholders, values = "", "", []
            for key, value in json_dict.items():
                columns = columns + key
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
            insert = f" INSERT INTO {table} ({columns}) VALUES ({values});"
            try:
                cur.execute(insert, values)
                conn.commit()
            except psycopg.Error as e:
                print(f"Database error: {e}")
                if conn:
                    conn.rollback() # Rollback in case of error
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            finally:
                if conn:
                    cur.close()
                    conn.close()
                    print("Database connection closed.")

            
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
