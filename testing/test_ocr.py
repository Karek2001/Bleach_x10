# test_ocr.py - OCR Testing Tool for Task System
import asyncio
import numpy as np
from PIL import Image
import cv2
import os
import sys
import glob
from typing import Dict, List, Tuple, Optional

# Import OCR components from actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from actions import ocr_manager

# Import task definitions
from tasks import (
    Main_Tasks, Restarting_Tasks, Shared_Tasks, Switcher_Tasks,
    GUILD_TUTORIAL_TASKS, Guild_Rejoin, Sell_Characters, HardStory_Tasks
)

class OCRTester:
    """Tool for testing OCR functionality on screenshots with task integration"""
    
    def __init__(self):
        self.test_image = None
        self.test_results = []
        self.current_screenshot_path = None
        self.available_tasks = {
            'main': Main_Tasks,
            'restarting': Restarting_Tasks,
            'shared': Shared_Tasks,
            'switcher': Switcher_Tasks,
            'guild_tutorial': GUILD_TUTORIAL_TASKS,
            'guild_rejoin': Guild_Rejoin,
            'sell_characters': Sell_Characters,
            'hard_story': HardStory_Tasks
        }
        
    def get_current_image_info(self):
        """Get information about currently loaded image"""
        if self.test_image is None:
            return "No image loaded"
        
        info = {
            'path': self.current_screenshot_path or 'Unknown',
            'dimensions': f"{self.test_image.shape[1]}x{self.test_image.shape[0]}",
            'channels': self.test_image.shape[2] if len(self.test_image.shape) > 2 else 1
        }
        return info
    
    def load_image(self, image_path: str) -> bool:
        """Load an image for testing"""
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return False
        
        try:
            # Load image
            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if img is None:
                print(f"❌ Failed to load image: {image_path}")
                return False
            
            # Convert BGR to RGB
            self.test_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.current_screenshot_path = image_path
            print(f"✅ Loaded image: {image_path}")
            print(f"   Dimensions: {self.test_image.shape[1]}x{self.test_image.shape[0]}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            return False
    
    async def test_region(self, roi: tuple = None, search_texts: list = None, 
                         show_preview: bool = True):
        """Test OCR on a specific region"""
        if self.test_image is None:
            print("❌ No image loaded. Use load_image() first.")
            return
        
        # Default to full image if no ROI specified
        if roi is None:
            roi = (0, 0, self.test_image.shape[1], self.test_image.shape[0])
        
        x, y, w, h = roi
        print(f"\n🔍 Testing OCR on region: x={x}, y={y}, width={w}, height={h}")
        
        # Extract text from region
        detected_texts = await ocr_manager.extract_text_from_region(self.test_image, roi)
        
        if not detected_texts:
            print("❌ No text detected in region")
            return
        
        print(f"✅ Found {len(detected_texts)} text elements:")
        print("-" * 50)
        
        for i, (text, position) in enumerate(detected_texts, 1):
            print(f"{i}. Text: '{text}'")
            print(f"   Position: {position}")
            
            # Check if text matches search terms
            if search_texts:
                for search in search_texts:
                    if search.lower() in text:
                        print(f"   ⭐ MATCH: Contains '{search}'")
        
        print("-" * 50)
        
        # Show preview if requested
        if show_preview:
            self.show_region_preview(roi, detected_texts)
        
        self.test_results = detected_texts
        return detected_texts
    
    def show_region_preview(self, roi: tuple, detected_texts: list):
        """Display the region with OCR results marked"""
        try:
            x, y, w, h = roi
            
            # Create a copy of the image
            preview = self.test_image.copy()
            
            # Draw ROI rectangle
            cv2.rectangle(preview, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Mark detected text positions
            for text, (cx, cy) in detected_texts:
                # Draw center point
                cv2.circle(preview, (cx, cy), 5, (255, 0, 0), -1)
                
                # Add text label
                cv2.putText(preview, text[:20], (cx+10, cy),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            # Convert RGB to BGR for OpenCV display
            preview_bgr = cv2.cvtColor(preview, cv2.COLOR_RGB2BGR)
            
            # Save preview image
            cv2.imwrite("ocr_preview.png", preview_bgr)
            print("📸 Preview saved as 'ocr_preview.png'")
            
            # Try to display (may not work in all environments)
            cv2.imshow("OCR Preview (Press any key to close)", preview_bgr)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            print(f"⚠️ Could not display preview: {e}")
            print("   Preview saved as 'ocr_preview.png'")
    
    async def test_with_task_templates(self, task_category: str = None):
        """Test OCR using task template images as reference"""
        if self.test_image is None:
            print("❌ No image loaded. Load an image first.")
            return
            
        print("\n🎯 Testing with task template matching...")
        
        # If specific category provided, test only that category
        if task_category and task_category in self.available_tasks:
            await self.test_task_ocr(task_category)
        else:
            # Test all categories
            for category in self.available_tasks.keys():
                print(f"\n--- Testing {category} tasks ---")
                await self.test_task_ocr(category)
    
    async def batch_test_regions(self, regions: list):
        """Test multiple regions"""
        if self.test_image is None:
            print("❌ No image loaded")
            return
        
        print(f"\n🔄 Testing {len(regions)} regions...")
        
        all_results = []
        for i, region_config in enumerate(regions, 1):
            roi = region_config.get("roi")
            search = region_config.get("search_texts", [])
            name = region_config.get("name", f"Region {i}")
            
            print(f"\n📍 {name}:")
            results = await self.test_region(roi, search, show_preview=False)
            all_results.append({
                "name": name,
                "roi": roi,
                "results": results
            })
        
        return all_results
    
    def create_task_from_result(self, text: str, position: tuple, 
                               task_name: str = "OCR Task"):
        """Create a task configuration from OCR result"""
        task = {
            "task_name": task_name,
            "type": "ocr",
            "ocr_text": text.lower(),
            "click_location_str": f"{position[0]},{position[1]}",
            "roi": [position[0]-50, position[1]-20, 100, 40],  # Estimate ROI around text
            "use_match_position": True,
            "priority": 10,
            "cooldown": 2.0
        }
        
        print("\n📝 Generated task configuration:")
        print("-" * 50)
        for key, value in task.items():
            print(f"  {key}: {value}")
        print("-" * 50)
        
        return task
    
    def list_local_screenshots(self, directory: str = ".") -> List[str]:
        """List available screenshot files in directory"""
        screenshot_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp']
        screenshots = []
        
        for ext in screenshot_extensions:
            screenshots.extend(glob.glob(os.path.join(directory, ext)))
            screenshots.extend(glob.glob(os.path.join(directory, '**', ext), recursive=True))
        
        return sorted(list(set(screenshots)))
    
    def list_available_tasks(self):
        """Display available task categories"""
        print("\n📋 Available Task Categories:")
        print("=" * 40)
        for i, (key, tasks) in enumerate(self.available_tasks.items(), 1):
            task_count = len(tasks) if isinstance(tasks, list) else "N/A"
            print(f"{i}. {key.replace('_', ' ').title()} ({task_count} tasks)")
        return list(self.available_tasks.keys())
    
    async def test_task_ocr(self, task_category: str, task_index: int = None):
        """Test OCR for specific tasks"""
        if self.test_image is None:
            print("❌ No image loaded. Load an image first.")
            return
            
        if task_category not in self.available_tasks:
            print(f"❌ Unknown task category: {task_category}")
            return
            
        tasks = self.available_tasks[task_category]
        if not isinstance(tasks, list):
            print(f"❌ Invalid task format for {task_category}")
            return
            
        if task_index is not None:
            if 0 <= task_index < len(tasks):
                tasks_to_test = [tasks[task_index]]
            else:
                print(f"❌ Task index {task_index} out of range (0-{len(tasks)-1})")
                return
        else:
            tasks_to_test = tasks
            
        print(f"\n🔍 Testing OCR for {task_category} tasks...")
        print("=" * 50)
        
        for i, task in enumerate(tasks_to_test):
            task_name = task.get('task_name', f'Task {i}')
            print(f"\n📝 Task: {task_name}")
            
            # Test based on task type
            if task.get('type') == 'template':
                await self._test_template_task(task)
            elif task.get('type') == 'pixel':
                await self._test_pixel_task(task)
            elif 'roi' in task:
                # Test OCR in the task's ROI
                roi = task['roi']
                if len(roi) == 4:
                    await self.test_region(tuple(roi), show_preview=False)
            else:
                print("   ⚠️ No testable OCR region found")
    
    async def _test_template_task(self, task: Dict):
        """Test OCR for template-based tasks"""
        roi = task.get('roi')
        template_path = task.get('template_path', '')
        
        print(f"   Template: {template_path}")
        if roi and len(roi) == 4:
            print(f"   ROI: {roi}")
            await self.test_region(tuple(roi), show_preview=False)
        else:
            print("   ⚠️ No ROI defined for template task")
    
    async def _test_pixel_task(self, task: Dict):
        """Test OCR for pixel-based tasks"""
        click_location = task.get('click_location_str', '')
        search_array = task.get('search_array', [])
        
        print(f"   Click Location: {click_location}")
        print(f"   Search Array: {len(search_array)} elements")
        
        # For pixel tasks, test OCR around the click location
        if click_location:
            try:
                x, y = map(int, click_location.split(','))
                # Create a ROI around the click point
                roi = (max(0, x-50), max(0, y-50), 100, 100)
                print(f"   Testing OCR around click point: {roi}")
                await self.test_region(roi, show_preview=False)
            except ValueError:
                print("   ⚠️ Invalid click location format")
    
    def interactive_mode(self):
        """Interactive mode for testing OCR with task integration"""
        print("\n🎯 OCR Interactive Testing Mode (Task-Integrated)")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Load image from file")
            print("2. List local screenshots")
            print("3. Test region (manual)")
            print("4. Test full image")
            print("5. List available tasks")
            print("6. Test specific task category")
            print("7. Test single task")
            print("8. Search for text")
            print("9. Show last results")
            print("10. Exit")
            
            choice = input("\nEnter choice (1-10): ").strip()
            
            if choice == '1':
                path = input("Enter image path: ").strip()
                self.load_image(path)
                
            elif choice == '2':
                screenshots = self.list_local_screenshots()
                if screenshots:
                    print("\n📸 Available Screenshots:")
                    for i, path in enumerate(screenshots, 1):
                        print(f"{i}. {path}")
                    try:
                        idx = int(input("\nSelect screenshot (number): ")) - 1
                        if 0 <= idx < len(screenshots):
                            self.load_image(screenshots[idx])
                    except ValueError:
                        print("❌ Invalid selection")
                else:
                    print("❌ No screenshots found")
                    
            elif choice == '3':
                if self.test_image is None:
                    print("❌ No image loaded. Load an image first.")
                    continue
                    
                try:
                    x = int(input("Enter X coordinate: "))
                    y = int(input("Enter Y coordinate: "))
                    w = int(input("Enter width: "))
                    h = int(input("Enter height: "))
                    
                    search_text = input("Enter text to search for (optional): ").strip()
                    search_texts = [search_text] if search_text else None
                    
                    asyncio.run(self.test_region((x, y, w, h), search_texts))
                except ValueError:
                    print("❌ Invalid coordinates. Please enter numbers.")
                    
            elif choice == '4':
                if self.test_image is None:
                    print("❌ No image loaded. Load an image first.")
                    continue
                    
                search_text = input("Enter text to search for (optional): ").strip()
                search_texts = [search_text] if search_text else None
                
                asyncio.run(self.test_region(search_texts=search_texts))
            
            elif choice == '5':
                self.list_available_tasks()
            
            elif choice == '6':
                task_keys = self.list_available_tasks()
                try:
                    idx = int(input("\nSelect task category (number): ")) - 1
                    if 0 <= idx < len(task_keys):
                        asyncio.run(self.test_task_ocr(task_keys[idx]))
                except ValueError:
                    print("❌ Invalid selection")
            
            elif choice == '7':
                task_keys = self.list_available_tasks()
                try:
                    cat_idx = int(input("\nSelect task category (number): ")) - 1
                    if 0 <= cat_idx < len(task_keys):
                        category = task_keys[cat_idx]
                        tasks = self.available_tasks[category]
                        if isinstance(tasks, list):
                            print(f"\n📋 Tasks in {category}:")
                            for i, task in enumerate(tasks):
                                print(f"{i+1}. {task.get('task_name', f'Task {i}')}")
                            task_idx = int(input("\nSelect task (number): ")) - 1
                            asyncio.run(self.test_task_ocr(category, task_idx))
                        else:
                            print("❌ Invalid task format")
                except ValueError:
                    print("❌ Invalid selection")
                    
            elif choice == '8':
                if self.test_image is None:
                    print("❌ No image loaded. Load an image first.")
                    continue
                    
                search_text = input("Enter text to search for: ").strip()
                if search_text:
                    asyncio.run(self.search_text(search_text))
                    
            elif choice == '9':
                self.show_last_results()
                
            elif choice == '10':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")


async def main():
    """Main test function with task integration examples"""
    tester = OCRTester()
    
    print("=" * 60)
    print("OCR TESTING TOOL - TASK INTEGRATED")
    print("=" * 60)
    
    # Check for local screenshots
    screenshots = tester.list_local_screenshots()
    if screenshots:
        print(f"\n📸 Found {len(screenshots)} local screenshots")
        print("Loading first available screenshot for demo...")
        if tester.load_image(screenshots[0]):
            # Demo: Test with task integration
            print("\n🎯 Demo: Testing main tasks OCR...")
            await tester.test_task_ocr('main', 0)  # Test first main task
            
            # Demo: Search for common game text
            print("\n🔍 Demo: Searching for common game text...")
            await tester.test_region(search_texts=["clear", "story", "quest", "next", "ok", "cancel"])
    else:
        print("\n📸 No local screenshots found.")
        print("Place some .png, .jpg, or .jpeg files in the current directory to test.")
    
    print("\n✅ Demo complete!")
    print("\n💡 Run with --interactive flag for full interactive mode:")
    print("   python test_ocr.py --interactive")


def interactive_mode():
    """Interactive OCR testing mode with task integration"""
    tester = OCRTester()
    tester.interactive_mode()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_mode()
        elif sys.argv[1] == "--dir" and len(sys.argv) > 2:
            # Test with specific directory
            async def test_directory():
                tester = OCRTester()
                image_dir = sys.argv[2]
                
                print(f"🔍 Searching for images in: {image_dir}")
                screenshots = tester.list_local_screenshots(image_dir)
                
                if not screenshots:
                    print("❌ No images found in directory")
                    return
                
                print(f"📸 Found {len(screenshots)} images")
                for i, img_path in enumerate(screenshots, 1):
                    print(f"\n{'='*50}")
                    print(f"Testing image {i}/{len(screenshots)}: {img_path}")
                    print(f"{'='*50}")
                    
                    if tester.load_image(img_path):
                        # Test with main tasks
                        await tester.test_task_ocr('main', 0)
                        
                        # Search for common text
                        await tester.test_region(search_texts=["clear", "story", "quest", "next", "ok"])
            
            asyncio.run(test_directory())
        else:
            print("Usage:")
            print("  python test_ocr.py                    # Demo mode")
            print("  python test_ocr.py --interactive      # Interactive mode")
            print("  python test_ocr.py --dir <path>       # Test all images in directory")
    else:
        asyncio.run(main())