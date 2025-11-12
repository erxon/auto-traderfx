import mt5_lib
import json

with open('settings.json', 'r') as f:
    settings = json.load(f)

if __name__ == "__main__":
    mt5_lib.connect_to_mt5()

    

