import json
import requests 
from bs4 import BeautifulSoup
import re


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
            #print(player_json)
        break


if __name__ == '__main__':
    main()
