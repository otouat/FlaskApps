from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/autocomplete')
def autocomplete():
    term = request.args.get('term')
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon?limit=1000')
    if response.status_code == 200:
        data = response.json()
        pokemon_names = [pokemon['name'] for pokemon in data['results']]
        suggestions = [name for name in pokemon_names if term.lower() in name.lower()]
        return jsonify(suggestions)
    return jsonify([])

@app.route('/search')
def search():
    pokemon_name = request.args.get('pokemon_name')
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}')
    
    stat_abbreviations = {
    "hp": "HP",
    "attack": "ATK",
    "defense": "DEF",
    "special-attack": "Sp. ATK",
    "special-defense": "Sp. DEF",
    "speed": "SPD"
    }
    
    if response.status_code == 200:
        data = response.json()
        name = data['name']
        types = [type_info['type']['name'] for type_info in data['types']]
        picture_url = data['sprites']['front_default']
        stats = data["stats"]
        print(data["sprites"])
        stat_table = []
        for stat in stats:
            stat_name = stat["stat"]["name"]
            base_stat = stat["base_stat"]
            abbreviated_name = stat_abbreviations.get(stat_name, stat_name.upper())
            stat_table.append({"name": abbreviated_name, "value": base_stat})  
            
        return render_template('results.html', name=name, types=types, picture_url=picture_url, stat_table=stat_table)
    
    return render_template('results.html', name="Pokémon not found", types=[], picture_url="",stat_table="")

if __name__ == '__main__':
    app.run(debug=True)
