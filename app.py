from flask import Flask, render_template, jsonify
import standings_cascade_points_desc as standings
import time

app = Flask(__name__)

# Cache global para los datos
# Almacenaremos los datos de la API y el momento de la última actualización
# Puedes usar un diccionario para esto.
cache = {
    "data": None,
    "last_updated": 0,
    "expires_in": 300 # 5 minutos en segundos
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/full")
def api_full():
    current_time = time.time()
    
    # Comprobar si la caché ha expirado
    if cache["data"] is None or (current_time - cache["last_updated"]) > cache["expires_in"]:
        print("Caché expirada o vacía. Consultando API...")
        try:
            # Llama a las funciones para obtener datos
            rows = standings.compute_rows()
            games_today = standings.games_played_today_scl()
            
            # Almacena los nuevos datos y actualiza el timestamp
            cache["data"] = {
                "standings": rows,
                "games_today": games_today
            }
            cache["last_updated"] = current_time
            print("Caché actualizada con nuevos datos.")
            
        except Exception as e:
            # En caso de error, si hay datos viejos en la caché, devuélvelos
            # Si la caché está vacía, devuelve un error 500
            if cache["data"] is not None:
                print(f"Error al consultar API: {e}. Sirviendo datos viejos de la caché.")
                return jsonify(cache["data"])
            else:
                print(f"Error fatal al consultar API y caché vacía: {e}")
                return jsonify({"error": "No se pudieron cargar los datos."}), 500
    else:
        # La caché aún está fresca, devuelve los datos sin llamar a la API
        print("Sirviendo datos desde la caché.")
        
    return jsonify(cache["data"])

if __name__ == "__main__":
    app.run(debug=True)
