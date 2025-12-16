#!/usr/bin/env python3
"""
Emotion-Adaptive Study Assistant - Main Entry Point
====================================================

This script provides a unified way to run all components of the system:
- Backend API (FastAPI)
- Frontend (Flask)
- Both together (recommended for development)

Usage:
    python run.py              # Run both backend and frontend
    python run.py --backend    # Run only the FastAPI backend
    python run.py --frontend   # Run only the Flask frontend
    python run.py --help       # Show help
"""

import argparse
import subprocess
import sys
import os
import threading
import time
import signal

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def run_backend():
    """Run the FastAPI backend server using uvicorn."""
    import uvicorn
    from app.api import app
    from app.database import init_db
    
    # Initialize database
    print("[Backend] Initializing database...")
    init_db()
    
    print("[Backend] Starting FastAPI server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


def run_frontend():
    """Run the Flask frontend server."""
    from frontend.flask_app import app, main
    main()


def run_backend_thread():
    """Run backend in a separate thread."""
    import uvicorn
    from app.api import app
    from app.database import init_db
    
    # Initialize database
    init_db()
    
    # Run uvicorn in a thread-safe way
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


def run_both():
    """Run both backend and frontend together."""
    print("\n" + "="*70)
    print("🎓 EMOTION-ADAPTIVE STUDY ASSISTANT")
    print("="*70)
    print("\nStarting both servers...")
    print("  • Backend (FastAPI):  http://localhost:8000")
    print("  • Frontend (Flask):   http://localhost:5002")
    print("\n👉 Open http://localhost:5002 in your browser to start studying!")
    print("="*70 + "\n")
    
    # Start backend in background thread
    backend_thread = threading.Thread(target=run_backend_thread, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(2)
    
    # Run frontend in main thread
    run_frontend()


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║   🎓 EMOTION-ADAPTIVE STUDY ASSISTANT                            ║
    ║                                                                   ║
    ║   An intelligent HCI system that adapts to your emotional state  ║
    ║   to enhance self-directed learning.                             ║
    ║                                                                   ║
    ║   Features:                                                       ║
    ║   • 📹 Facial emotion detection (OpenCV + DeepFace)              ║
    ║   • 🎤 Voice sentiment analysis (Librosa)                        ║
    ║   • 🧠 Multimodal emotion fusion                                 ║
    ║   • 💡 Adaptive interventions (hints, breaks, challenges)        ║
    ║   • 📊 Learning progress tracking                                ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Emotion-Adaptive Study Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py              Run both backend and frontend (recommended)
  python run.py --backend    Run only the FastAPI backend API
  python run.py --frontend   Run only the Flask frontend UI
  python run.py --init-db    Initialize the database only

For more information, see README.md
        """
    )
    
    parser.add_argument(
        '--backend', 
        action='store_true',
        help='Run only the FastAPI backend server (port 8000)'
    )
    
    parser.add_argument(
        '--frontend', 
        action='store_true',
        help='Run only the Flask frontend server (port 5002)'
    )
    
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database tables only (no server)'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Suppress the startup banner'
    )
    
    args = parser.parse_args()
    
    # Print banner unless suppressed
    if not args.no_banner:
        print_banner()
    
    # Handle different run modes
    if args.init_db:
        from app.database import init_db
        print("Initializing database...")
        init_db()
        print("✅ Database initialized successfully!")
        return
    
    if args.backend:
        run_backend()
    elif args.frontend:
        run_frontend()
    else:
        # Default: run both
        run_both()


if __name__ == "__main__":
    main()

