"""
PyHWP-based HWP controller for better HWP file manipulation.
This is an alternative to the COM-based approach.
"""

import os
import sys
from typing import Optional, List, Dict, Any
import tempfile
import shutil

try:
    import hwp5
    from hwp5.storage import open_storage_item
    from hwp5.xmlmodel import Hwp5File
    PYHWP_AVAILABLE = True
except ImportError as e:
    print(f"PyHWP not available: {e}")
    PYHWP_AVAILABLE = False

try:
    import hwp_extract
    HWP_EXTRACT_AVAILABLE = True
except ImportError as e:
    print(f"HWP Extract not available: {e}")
    HWP_EXTRACT_AVAILABLE = False


class PyHWPController:
    """
    HWP controller using pyhwp library for better file manipulation.
    """
    
    def __init__(self):
        self.current_file_path: Optional[str] = None
        self.hwp_storage = None
        self.document_text: Optional[str] = None
        self.is_loaded = False
        
    def check_availability(self) -> Dict[str, bool]:
        """Check which HWP libraries are available."""
        return {
            "pyhwp": PYHWP_AVAILABLE,
            "hwp_extract": HWP_EXTRACT_AVAILABLE
        }
    
    def open_file(self, file_path: str) -> bool:
        """
        Open an HWP file using pyhwp.
        
        Args:
            file_path (str): Path to the HWP file
            
        Returns:
            bool: Success status
        """
        try:
            if not PYHWP_AVAILABLE:
                print("PyHWP library is not available")
                return False
                
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            print(f"Opening HWP file with PyHWP: {file_path}")

            # Open the HWP file using Hwp5File
            self.hwp_storage = Hwp5File(file_path)
            self.current_file_path = file_path
            self.is_loaded = True

            print(f"Successfully opened HWP file: {file_path}")
            return True
            
        except Exception as e:
            print(f"Failed to open HWP file with PyHWP: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_text(self) -> Optional[str]:
        """
        Extract text content from the HWP file using XML events method.

        Returns:
            str: Extracted text content
        """
        try:
            if not self.is_loaded or not self.hwp_storage:
                print("No HWP file loaded")
                return None

            print("Extracting text from HWP file using XML events...")

            # Get BodyText sections
            sections = self.hwp_storage['BodyText']

            # Use XML events to extract text content
            xml_events = list(sections.xmlevents())
            print(f"Processing {len(xml_events)} XML events...")

            text_content = []

            for event in xml_events:
                # Look for text-containing events
                if isinstance(event, tuple) and len(event) >= 2:
                    event_type, event_data = event[0], event[1]

                    # Check if event_data is text content
                    if isinstance(event_data, str) and len(event_data.strip()) > 0:
                        # Filter out structural elements
                        if event_data.strip() not in [
                            'PageDef', 'FootnoteShape', 'PageBorderFill', 'Border',
                            'ColumnsDef', 'PageNumberPosition', 'Text', 'ControlChar',
                            'LineSeg', 'Paragraph', 'TableCell', 'TableRow', 'TableBody',
                            'TableControl', 'ZoneInfo', 'Array', 'ControlData', 'SectionDef',
                            'BodyText', 'ColumnSet'
                        ]:
                            text_content.append(event_data)

            # Join all text content
            self.document_text = '\n'.join(text_content)
            print(f"Extracted {len(self.document_text)} characters of text")

            # Show preview of extracted text
            if len(self.document_text) > 0:
                print(f"Text preview (first 500 chars): {self.document_text[:500]}")

            return self.document_text

        except Exception as e:
            print(f"Failed to extract text: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def find_text_positions(self, search_text: str) -> List[int]:
        """
        Find all positions of a text string in the document.
        
        Args:
            search_text (str): Text to search for
            
        Returns:
            List[int]: List of character positions where text was found
        """
        try:
            if not self.document_text:
                self.extract_text()
            
            if not self.document_text:
                return []
            
            positions = []
            start = 0
            while True:
                pos = self.document_text.find(search_text, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            print(f"Found '{search_text}' at {len(positions)} positions: {positions}")
            return positions
            
        except Exception as e:
            print(f"Failed to find text positions: {e}")
            return []
    
    def replace_text_in_content(self, find_text: str, replace_text: str) -> bool:
        """
        Replace text in the extracted content (in memory only).

        Args:
            find_text (str): Text to find
            replace_text (str): Text to replace with

        Returns:
            bool: Success status
        """
        try:
            if not self.document_text:
                self.extract_text()

            if not self.document_text:
                print("No document text available")
                return False

            if find_text not in self.document_text:
                print(f"Text not found: '{find_text}'")
                return False

            # Replace text in memory
            old_text = self.document_text
            self.document_text = self.document_text.replace(find_text, replace_text)

            replacements = old_text.count(find_text)
            print(f"Replaced {replacements} occurrences of '{find_text}' with '{replace_text}'")
            return True

        except Exception as e:
            print(f"Failed to replace text: {e}")
            return False

    def create_modified_hwp(self, output_path: str) -> bool:
        """
        Create a new HWP file with the modified text content.
        Currently creates a text file with the modified content.

        Args:
            output_path (str): Path for the new HWP file

        Returns:
            bool: Success status
        """
        try:
            if not self.document_text:
                print("No modified text content available")
                return False

            print(f"Creating modified content file: {output_path}")

            # Method 1: Create a text file with the modified content
            try:
                # Create text version with modified content
                text_output_path = output_path.replace('.hwp', '_modified.txt')
                with open(text_output_path, 'w', encoding='utf-8') as f:
                    f.write(self.document_text)

                print(f"✅ Created text version: {text_output_path}")

                # Method 2: Copy original file for reference
                import shutil
                backup_path = output_path.replace('.hwp', '_original_backup.hwp')
                shutil.copy2(self.current_file_path, backup_path)
                print(f"✅ Created backup: {backup_path}")

                print("📋 Summary:")
                print(f"  - Modified text content: {text_output_path}")
                print(f"  - Original backup: {backup_path}")
                print("  - Note: Full HWP binary reconstruction requires advanced format knowledge")

                return True

            except Exception as e1:
                print(f"File creation failed: {e1}")
                return False

        except Exception as e:
            print(f"Failed to create modified files: {e}")
            return False

    def batch_replace_text(self, replacements: Dict[str, str]) -> int:
        """
        Replace multiple text patterns in the document.

        Args:
            replacements (Dict[str, str]): Dictionary of find->replace pairs

        Returns:
            int: Total number of replacements made
        """
        try:
            if not self.document_text:
                self.extract_text()

            if not self.document_text:
                print("No document text available")
                return 0

            total_replacements = 0

            for find_text, replace_text in replacements.items():
                if find_text in self.document_text:
                    count = self.document_text.count(find_text)
                    self.document_text = self.document_text.replace(find_text, replace_text)
                    total_replacements += count
                    print(f"✅ Replaced {count} occurrences of '{find_text}' with '{replace_text}'")
                else:
                    print(f"❌ Text not found: '{find_text}'")

            print(f"📋 Total replacements made: {total_replacements}")
            return total_replacements

        except Exception as e:
            print(f"Failed to batch replace text: {e}")
            return 0
    
    def get_document_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded document.
        
        Returns:
            Dict: Document information
        """
        try:
            if not self.is_loaded or not self.hwp_storage:
                return {"error": "No document loaded"}

            info = {
                "file_path": self.current_file_path,
                "is_loaded": self.is_loaded,
                "has_text": bool(self.document_text),
                "text_length": len(self.document_text) if self.document_text else 0,
                "pyhwp_available": PYHWP_AVAILABLE,
                "hwp_extract_available": HWP_EXTRACT_AVAILABLE
            }

            # Try to get additional info from the HWP storage
            try:
                info["storage_items"] = list(self.hwp_storage)
            except:
                pass

            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def close(self):
        """Close the HWP file and clean up resources."""
        try:
            if self.hwp_storage:
                self.hwp_storage.close()

            self.hwp_storage = None
            self.current_file_path = None
            self.document_text = None
            self.is_loaded = False

            print("PyHWP controller closed successfully")

        except Exception as e:
            print(f"Error closing PyHWP controller: {e}")


def test_pyhwp_controller():
    """Test function for the PyHWP controller."""
    controller = PyHWPController()

    print("=== PyHWP Controller Test ===")
    print(f"Library availability: {controller.check_availability()}")

    # Test with a sample file
    test_file = "C:\\work\\hwp-mcp\\template.hwp"
    if os.path.exists(test_file):
        print(f"\nTesting with file: {test_file}")

        if controller.open_file(test_file):
            print("✅ File opened successfully")

            # Get document info
            info = controller.get_document_info()
            print(f"Document info: {info}")

            # Extract text
            text = controller.extract_text()
            if text:
                print(f"✅ Text extracted: {len(text)} characters")
                print(f"First 200 characters: {text[:200]}...")

                # Test text search
                positions = controller.find_text_positions("Application Form")
                print(f"✅ Found 'Application Form' at positions: {positions}")

                # Test batch text replacement
                replacements = {
                    "TE25****": "TE250235",
                    "yyyy. mm. dd.": "2025. 01. 15.",
                    "Open Call Project[   ]": "Open Call Project[ ✓ ]"
                }

                total_replaced = controller.batch_replace_text(replacements)
                if total_replaced > 0:
                    print(f"✅ Batch replacement successful: {total_replaced} total replacements")

                    # Test file creation
                    output_path = "C:\\work\\hwp-mcp\\template_filled.hwp"
                    if controller.create_modified_hwp(output_path):
                        print("✅ Modified files created successfully")
                    else:
                        print("❌ File creation failed")
                else:
                    print("❌ No replacements made")
            else:
                print("❌ Text extraction failed")
        else:
            print("❌ Failed to open file")

        controller.close()
    else:
        print(f"Test file not found: {test_file}")


if __name__ == "__main__":
    test_pyhwp_controller()
