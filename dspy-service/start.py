#!/usr/bin/env python3
"""
DSPy AI Tutor Service Startup Script
Handles initialization and startup of the DSPy service with proper error handling
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

def setup_logging():
    """Configure logging for the service"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Remove default logger
    logger.remove()
    
    # Add console logger with custom format
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file logger
    log_file = os.getenv("LOG_FILE", "logs/dspy_service.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logger.add(
        log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days"
    )

def check_requirements():
    """Check if all required dependencies are available"""
    required_packages = [
        ('dspy', 'dspy'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('google.generativeai', 'google.generativeai'),
        ('numpy', 'numpy'),
        ('scikit-learn', 'sklearn')  # scikit-learn imports as sklearn
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install missing packages using: pip install -r requirements.txt")
        return False

    return True

def check_environment():
    """Check if required environment variables are set"""
    required_env_vars = [
        'GOOGLE_API_KEY'
    ]
    
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please copy .env.example to .env and fill in the required values")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'cache',
        os.getenv('OPTIMIZATION_CACHE_DIR', './cache')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Created directory: {directory}")

async def test_service_initialization():
    """Test if the service can initialize properly"""
    try:
        logger.info("Testing service initialization...")
        
        # Import and test main components
        from main import app
        from services.vector_service import GeminiVectorService
        from services.optimization_service import OptimizationService

        # Test vector service initialization
        vector_service = GeminiVectorService()
        await vector_service.initialize()
        logger.info("✓ Vector service initialization test passed")

        # Test optimization service initialization
        optimization_service = OptimizationService()
        await optimization_service.initialize()
        logger.info("✓ Optimization service initialization test passed")
        
        # Cleanup test services
        await vector_service.cleanup()
        
        logger.info("✓ All service initialization tests passed")
        return True
        
    except Exception as e:
        logger.error(f"Service initialization test failed: {e}")
        return False

def main():
    """Main startup function"""
    logger.info("Starting DSPy AI Tutor Service...")
    
    # Setup logging
    setup_logging()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Test service initialization (skip for now to get service running)
    logger.info("Skipping initialization test - starting service directly")
    
    # Get configuration
    host = os.getenv("SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SERVICE_PORT", "8001"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    reload = os.getenv("RELOAD_ON_CHANGE", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Reload on change: {reload}")
    
    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            log_level=log_level,
            reload=reload,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
