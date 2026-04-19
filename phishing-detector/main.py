import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from utils.logger import get_logger
import config

logger = get_logger(__name__)

def main():
    """Main entry point"""
    logger.info("Starting Phishing Email Detector")
    
    # Check API key
    if not config.DEMO_MODE and not config.OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not set!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=sk-...")
        sys.exit(1)
    
    if config.DEMO_MODE:
        print("ℹ️  Running in DEMO MODE - No API calls will be made")
        logger.info("Running in DEMO MODE")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    logger.info("Application started successfully")
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
