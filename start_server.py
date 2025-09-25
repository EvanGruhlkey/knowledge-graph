"""
Startup script for the Knowledge Graph API server
"""

import uvicorn
import sys
import os

def main():
    """Start the FastAPI server with optimal settings"""
    print(" Starting Adaptive Personal Knowledge Graph API...")
    print(" Server will be available at: http://localhost:8000")
    print(" API Documentation: http://localhost:8000/docs")
    print(" Auto-reload enabled for development")
    print("\nPress Ctrl+C to stop the server\n")
    print("TIP: Tip: Use 'py' instead of 'python' on Windows!")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n Server stopped gracefully")
    except Exception as e:
        print(f"ERROR: Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
