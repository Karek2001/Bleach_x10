# OCR Usage Examples - Enhanced Number Extraction
"""
This file demonstrates how to use the enhanced OCR functionality
with the new is_id flag for different types of number extraction.
"""

import asyncio
import numpy as np
from actions import ocr_manager

async def extract_regular_numbers_example():
    """
    Example: Extract regular numbers like "21,124" or "1,000,000"
    Use is_id=False for numbers with comma separators
    """
    # Assuming you have a screenshot and ROI coordinates
    screenshot = np.array([])  # Your screenshot here
    roi = (x, y, width, height)  # Your region of interest
    
    # For numbers like "21,124"
    result = await ocr_manager.extract_numbers_enhanced(screenshot, roi, is_id=False)
    print(f"Regular number extracted: {result}")
    
    return result

async def extract_id_numbers_example():
    """
    Example: Extract ID numbers like "ID: 88 534 886"
    Use is_id=True for ID format with spaces between number groups
    """
    # Assuming you have a screenshot and ROI coordinates
    screenshot = np.array([])  # Your screenshot here
    roi = (x, y, width, height)  # Your region of interest
    
    # For IDs like "ID: 88 534 886"  
    result = await ocr_manager.extract_numbers_enhanced(screenshot, roi, is_id=True)
    print(f"ID extracted: {result}")
    
    return result

async def batch_number_extraction_example():
    """
    Example: Extract multiple different types of numbers from different regions
    """
    screenshot = np.array([])  # Your screenshot here
    
    # Define different regions and their expected content types
    regions = [
        ((100, 200, 150, 30), False),  # Regular number region
        ((300, 150, 200, 40), True),   # ID region
        ((50, 400, 120, 25), False),   # Another regular number
    ]
    
    results = []
    for roi, is_id_format in regions:
        result = await ocr_manager.extract_numbers_enhanced(screenshot, roi, is_id=is_id_format)
        results.append(result)
        print(f"Extracted {'ID' if is_id_format else 'number'}: {result}")
    
    return results

# Example usage in actual game tasks:
async def game_currency_detection():
    """
    Example: Detect game currency amounts
    """
    screenshot = np.array([])  # Your screenshot here
    currency_roi = (500, 50, 200, 30)  # Top right corner where currency is shown
    
    # Extract currency amount (regular number format)
    currency = await ocr_manager.extract_numbers_enhanced(screenshot, currency_roi, is_id=False)
    
    # Convert to integer for comparison
    try:
        currency_value = int(currency.replace(',', '')) if currency else 0
        print(f"Current currency: {currency} ({currency_value})")
        return currency_value
    except ValueError:
        print(f"Could not parse currency: {currency}")
        return 0

async def player_id_detection():
    """
    Example: Detect player ID from profile screen
    """
    screenshot = np.array([])  # Your screenshot here
    id_roi = (100, 300, 300, 50)  # Area where player ID is displayed
    
    # Extract player ID (ID format)
    player_id = await ocr_manager.extract_numbers_enhanced(screenshot, id_roi, is_id=True)
    print(f"Player ID: {player_id}")
    
    return player_id

# Integration with existing task system
def create_ocr_task_with_enhanced_numbers(roi, is_id_format=False):
    """
    Helper function to create OCR tasks that use the enhanced number extraction
    """
    return {
        "task_name": f"Extract {'ID' if is_id_format else 'Numbers'} from ROI",
        "type": "enhanced_ocr_numbers",
        "roi": roi,
        "is_id": is_id_format,
        "cooldown": 1.0
    }

if __name__ == "__main__":
    # Example of how to run these functions
    print("OCR Enhanced Number Extraction Examples")
    print("======================================")
    print()
    print("Usage:")
    print("# For numbers like '21,124'")
    print("result = await ocr_manager.extract_numbers_enhanced(screenshot, roi, is_id=False)")
    print()
    print("# For IDs like 'ID: 88 534 886'")
    print("result = await ocr_manager.extract_numbers_enhanced(screenshot, roi, is_id=True)")
    print()
    print("Key Features:")
    print("- Multiple preprocessing strategies for better accuracy")
    print("- Automatic confidence scoring and best result selection")
    print("- OCR artifact cleanup (l->1, O->0, etc.)")
    print("- Proper formatting for both number types")
    print("- Support for both EasyOCR and Tesseract backends")
