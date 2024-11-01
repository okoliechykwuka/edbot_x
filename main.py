from server import TheoriqServer

# Create the app at module level
server = TheoriqServer()
app = server.create_app()

def main():
    """
    Main function to run the Flask application directly
    """
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()