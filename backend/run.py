import sys
import traceback
import os
from app import create_app

try:
    app = create_app()
except Exception as e:
    print(f"Error creating app: {e}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')

    try:
        app.run(debug=True, host=host, port=port, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e) or "Port" in str(e):
            print(f"\nError: Port {port} is already in use.", file=sys.stderr)
            print("Please stop the other process or set FLASK_RUN_PORT to a different port.", file=sys.stderr)
            print(f"To find the process using port {port}, run: lsof -ti:{port}", file=sys.stderr)
        else:
            print(f"OS Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error running app: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
