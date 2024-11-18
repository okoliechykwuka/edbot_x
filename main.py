from server import TheoriqServer
from flask import jsonify

# Create the app at module level
server = TheoriqServer()
app = server.create_app()

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Edbot RAG Agent"})

def main():
    """
    Main function to run the Flask application directly
    """
    app.run(host="0.0.0.0", port=8000, threaded=True)

if __name__ == "__main__":
    main()