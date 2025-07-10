import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_logger(name):
    """Get a logger instance with the given name
    
    Args:
        name (str): Name for the logger
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

def format_error_response(error, status_code=500):
    """Format error response
    
    Args:
        error (Exception): The error that occurred
        status_code (int): HTTP status code
        
    Returns:
        tuple: (response_dict, status_code)
    """
    return {"error": str(error)}, status_code
