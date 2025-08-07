"""
Hybrid HWP Controller - Combines PyHWP for text extraction with COM for file manipulation.
This approach uses the strengths of both systems:
- PyHWP: Reliable text extraction and analysis
- COM: Working file operations and saving
"""

import os
import sys
from typing import Optional, List, Dict, Any

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.pyhwp_controller import PyHWPController
from tools.hwp_controller import HwpController


class HybridHWPController:
    """
    Hybrid HWP controller that combines PyHWP and COM automation.
    Uses PyHWP for reliable text extraction and COM for file operations.
    """
    
    def __init__(self):
        self.pyhwp_controller = PyHWPController()
        self.com_controller = HwpController()
        self.current_file_path: Optional[str] = None
        self.extracted_text: Optional[str] = None
        self.replacements_made: Dict[str, str] = {}
        
    def check_availability(self) -> Dict[str, bool]:
        """Check availability of both systems."""
        pyhwp_status = self.pyhwp_controller.check_availability()

        # Check COM availability by trying to connect
        com_available = self.com_controller.connect(visible=False)
        if com_available:
            self.com_controller.disconnect()

        return {
            "pyhwp_available": pyhwp_status.get("pyhwp", False),
            "hwp_extract_available": pyhwp_status.get("hwp_extract", False),
            "com_available": com_available,
            "hybrid_ready": (pyhwp_status.get("pyhwp", False) and com_available)
        }
    
    def open_file(self, file_path: str) -> bool:
        """
        Open HWP file using both systems.
        
        Args:
            file_path (str): Path to the HWP file
            
        Returns:
            bool: Success status
        """
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            print(f"Opening file with hybrid controller: {file_path}")
            
            # Open with PyHWP for text extraction
            pyhwp_success = self.pyhwp_controller.open_file(file_path)
            if not pyhwp_success:
                print("❌ Failed to open with PyHWP")
                return False
            
            # Connect and open with COM for file operations
            if not self.com_controller.connect(visible=False):
                print("❌ Failed to connect to COM")
                self.pyhwp_controller.close()
                return False

            com_success = self.com_controller.open_document(file_path)
            if not com_success:
                print("❌ Failed to open with COM")
                self.pyhwp_controller.close()
                self.com_controller.disconnect()
                return False
            
            self.current_file_path = file_path
            print("✅ File opened successfully with both systems")
            return True
            
        except Exception as e:
            print(f"Failed to open file: {e}")
            return False
    
    def extract_and_analyze_text(self) -> Optional[str]:
        """
        Extract text using PyHWP and analyze content.
        
        Returns:
            str: Extracted text content
        """
        try:
            print("Extracting text using PyHWP...")
            self.extracted_text = self.pyhwp_controller.extract_text()
            
            if self.extracted_text:
                print(f"✅ Extracted {len(self.extracted_text)} characters")
                print(f"Preview: {self.extracted_text[:200]}...")
                return self.extracted_text
            else:
                print("❌ Text extraction failed")
                return None
                
        except Exception as e:
            print(f"Text extraction error: {e}")
            return None
    
    def find_replaceable_patterns(self, patterns: List[str]) -> Dict[str, List[int]]:
        """
        Find all occurrences of patterns in the extracted text.
        
        Args:
            patterns (List[str]): List of text patterns to find
            
        Returns:
            Dict[str, List[int]]: Dictionary mapping patterns to their positions
        """
        try:
            if not self.extracted_text:
                self.extract_and_analyze_text()
            
            if not self.extracted_text:
                return {}
            
            results = {}
            for pattern in patterns:
                positions = self.pyhwp_controller.find_text_positions(pattern)
                results[pattern] = positions
                
            return results
            
        except Exception as e:
            print(f"Pattern finding error: {e}")
            return {}
    
    def perform_replacements_via_recreation(self, replacements: Dict[str, str]) -> bool:
        """
        Perform text replacements by recreating the document with modified content.

        Args:
            replacements (Dict[str, str]): Dictionary of find->replace pairs

        Returns:
            bool: Success status
        """
        try:
            print(f"Performing {len(replacements)} replacements via document recreation...")

            # First, modify the extracted text using pyhwp
            if not self.extracted_text:
                print("❌ No extracted text available")
                return False

            modified_text = self.extracted_text
            total_replacements = 0

            for find_text, replace_text in replacements.items():
                if find_text in modified_text:
                    count = modified_text.count(find_text)
                    modified_text = modified_text.replace(find_text, replace_text)
                    total_replacements += count
                    self.replacements_made[find_text] = replace_text
                    print(f"✅ Replaced {count} occurrences of '{find_text}' with '{replace_text}'")
                else:
                    print(f"❌ Text not found: '{find_text}'")

            if total_replacements == 0:
                print("❌ No replacements made")
                return False

            # Now create a new document with the modified text
            print("Creating new document with modified content...")

            # Close current document and create new one
            if not self.com_controller.create_new_document():
                print("❌ Failed to create new document")
                return False

            # Insert the modified text
            if not self.com_controller.insert_text(modified_text):
                print("❌ Failed to insert modified text")
                return False

            print(f"✅ Successfully created document with {total_replacements} replacements")
            return True

        except Exception as e:
            print(f"Replacement via recreation error: {e}")
            return False
    
    def save_file(self, output_path: Optional[str] = None) -> bool:
        """
        Save the modified file using COM.
        
        Args:
            output_path (Optional[str]): Path to save the file. If None, saves to current path.
            
        Returns:
            bool: Success status
        """
        try:
            if output_path:
                print(f"Saving file to: {output_path}")
                result = self.com_controller.save_document(output_path)
            else:
                print("Saving file...")
                result = self.com_controller.save_document()

            if result:
                print("✅ File saved successfully")
                return True
            else:
                print("❌ Save failed")
                return False
                
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of both controllers."""
        return {
            "file_path": self.current_file_path,
            "text_extracted": bool(self.extracted_text),
            "text_length": len(self.extracted_text) if self.extracted_text else 0,
            "replacements_made": len(self.replacements_made),
            "replacement_details": self.replacements_made,
            "availability": self.check_availability()
        }
    
    def close(self):
        """Close both controllers."""
        try:
            self.pyhwp_controller.close()
            self.com_controller.disconnect()

            self.current_file_path = None
            self.extracted_text = None
            self.replacements_made = {}

            print("✅ Hybrid controller closed successfully")

        except Exception as e:
            print(f"Error closing hybrid controller: {e}")


def test_hybrid_controller():
    """Test the hybrid controller."""
    controller = HybridHWPController()
    
    print("=== Hybrid HWP Controller Test ===")
    availability = controller.check_availability()
    print(f"System availability: {availability}")
    
    if not availability["hybrid_ready"]:
        print("❌ Hybrid system not ready - missing components")
        return
    
    # Test file
    test_file = "C:\\work\\hwp-mcp\\template.hwp"
    output_file = "C:\\work\\hwp-mcp\\template_hybrid_filled.hwp"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    try:
        # Open file
        if controller.open_file(test_file):
            print("✅ File opened with hybrid system")
            
            # Extract and analyze text
            text = controller.extract_and_analyze_text()
            if text:
                # Find patterns
                patterns = ["TE25****", "yyyy. mm. dd.", "Open Call Project[   ]"]
                found_patterns = controller.find_replaceable_patterns(patterns)
                print(f"Found patterns: {found_patterns}")
                
                # Perform replacements
                replacements = {
                    "TE25****": "TE250235",
                    "yyyy. mm. dd.": "2025. 01. 15.",
                    "Open Call Project[   ]": "Open Call Project[ ✓ ]"
                }
                
                if controller.perform_replacements_via_recreation(replacements):
                    print("✅ Replacements completed")
                    
                    # Save file
                    if controller.save_file(output_file):
                        print(f"✅ File saved: {output_file}")
                        
                        # Show final status
                        status = controller.get_status()
                        print(f"Final status: {status}")
                    else:
                        print("❌ Failed to save file")
                else:
                    print("❌ Replacements failed")
            else:
                print("❌ Text extraction failed")
        else:
            print("❌ Failed to open file")
            
    finally:
        controller.close()


if __name__ == "__main__":
    test_hybrid_controller()
