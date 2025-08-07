"""
Clipboard-based HWP Controller - Uses clipboard operations for reliable text access
"""

import win32com.client
import win32clipboard
import os
from typing import Optional, Dict, List


class ClipboardHWPController:
    """
    HWP controller that uses clipboard operations for reliable text access and replacement.
    """
    
    def __init__(self):
        self.hwp = None
        self.current_file_path: Optional[str] = None
        self.document_text: Optional[str] = None
        self.is_connected = False
        
    def connect(self, visible: bool = True) -> bool:
        """Connect to HWP application."""
        try:
            self.hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
            if visible:
                self.hwp.XHwpWindows.Item(0).Visible = True
            self.is_connected = True
            print("✅ Connected to HWP")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to HWP: {e}")
            return False
    
    def open_document(self, file_path: str) -> bool:
        """Open HWP document."""
        try:
            if not self.is_connected:
                if not self.connect():
                    return False
            
            result = self.hwp.Open(file_path, "HWP", "")
            if result:
                self.current_file_path = file_path
                print(f"✅ Opened: {file_path} (Pages: {self.hwp.PageCount})")
                return True
            else:
                print(f"❌ Failed to open: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error opening document: {e}")
            return False
    
    def extract_text_via_clipboard(self) -> Optional[str]:
        """Extract document text using clipboard operations."""
        try:
            if not self.hwp:
                print("❌ HWP not connected")
                return None
            
            print("Extracting text via clipboard...")
            
            # Select all content
            self.hwp.HAction.Run("SelectAll")
            
            # Copy to clipboard
            self.hwp.HAction.Run("Copy")
            
            # Clear selection
            self.hwp.HAction.Run("Cancel")
            
            # Get clipboard content
            win32clipboard.OpenClipboard()
            try:
                clipboard_data = win32clipboard.GetClipboardData()
                self.document_text = str(clipboard_data)
                
                print(f"✅ Extracted {len(self.document_text)} characters via clipboard")
                return self.document_text
                
            except Exception as e:
                print(f"❌ Failed to read clipboard: {e}")
                return None
            finally:
                win32clipboard.CloseClipboard()
                
        except Exception as e:
            print(f"❌ Clipboard extraction failed: {e}")
            return None
    
    def find_text_positions(self, search_text: str) -> List[int]:
        """Find all positions of search text in document."""
        if not self.document_text:
            self.extract_text_via_clipboard()
        
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
        
        return positions
    
    def replace_text_via_recreation(self, replacements: Dict[str, str]) -> bool:
        """Replace text by recreating document with modified content."""
        try:
            if not self.document_text:
                self.extract_text_via_clipboard()
            
            if not self.document_text:
                print("❌ No document text available")
                return False
            
            print(f"Performing {len(replacements)} replacements...")
            
            # Apply replacements to text
            modified_text = self.document_text
            total_replacements = 0
            
            for find_text, replace_text in replacements.items():
                if find_text in modified_text:
                    count = modified_text.count(find_text)
                    modified_text = modified_text.replace(find_text, replace_text)
                    total_replacements += count
                    print(f"✅ Replaced {count} occurrences of '{find_text}' with '{replace_text}'")
                else:
                    print(f"❌ Text not found: '{find_text}'")
            
            if total_replacements == 0:
                print("❌ No replacements made")
                return False
            
            # Clear current document and insert modified text
            print("Recreating document with modified content...")
            
            # Select all and delete
            self.hwp.HAction.Run("SelectAll")
            self.hwp.HAction.Run("Delete")
            
            # Insert modified text
            self.hwp.HAction.GetDefault("InsertText", self.hwp.HParameterSet.HInsertText.HSet)
            insert_pset = self.hwp.HParameterSet.HInsertText
            insert_pset.Text = modified_text
            
            result = self.hwp.HAction.Execute("InsertText", insert_pset.HSet)
            
            if result:
                print(f"✅ Successfully recreated document with {total_replacements} replacements")
                return True
            else:
                print("❌ Failed to insert modified text")
                return False
                
        except Exception as e:
            print(f"❌ Text replacement failed: {e}")
            return False
    
    def save_document(self, output_path: Optional[str] = None) -> bool:
        """Save the document."""
        try:
            if output_path:
                result = self.hwp.SaveAs(output_path, "HWP", "")
                if result:
                    print(f"✅ Saved to: {output_path}")
                    return True
                else:
                    print(f"❌ Failed to save to: {output_path}")
                    return False
            else:
                result = self.hwp.Save()
                if result:
                    print("✅ Document saved")
                    return True
                else:
                    print("❌ Failed to save document")
                    return False
                    
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def get_document_info(self) -> Dict:
        """Get document information."""
        return {
            "file_path": self.current_file_path,
            "is_connected": self.is_connected,
            "has_text": bool(self.document_text),
            "text_length": len(self.document_text) if self.document_text else 0,
            "page_count": self.hwp.PageCount if self.hwp else 0
        }
    
    def disconnect(self):
        """Disconnect from HWP."""
        try:
            if self.hwp:
                # Don't close HWP application, just disconnect
                self.hwp = None
            
            self.is_connected = False
            self.current_file_path = None
            self.document_text = None
            
            print("✅ Disconnected from HWP")
            
        except Exception as e:
            print(f"❌ Disconnect error: {e}")


def test_clipboard_controller():
    """Test the clipboard-based HWP controller."""
    controller = ClipboardHWPController()
    
    print("=== Clipboard HWP Controller Test ===")
    
    test_file = "C:\\work\\hwp-mcp\\template.hwp"
    output_file = "C:\\work\\hwp-mcp\\template_clipboard_filled.hwp"
    
    try:
        # Connect and open
        if controller.open_document(test_file):
            
            # Extract text
            text = controller.extract_text_via_clipboard()
            if text:
                print(f"✅ Text extracted: {len(text)} characters")
                
                # Find target patterns
                targets = ["TE25****", "yyyy. mm. dd.", "Open Call Project[   ]"]
                for target in targets:
                    positions = controller.find_text_positions(target)
                    print(f"Found '{target}' at positions: {positions}")
                
                # Perform replacements
                replacements = {
                    "TE25****": "TE250235",
                    "yyyy. mm. dd.": "2025. 01. 15.",
                    "Open Call Project[   ]": "Open Call Project[ ✓ ]"
                }
                
                if controller.replace_text_via_recreation(replacements):
                    print("✅ Replacements completed")
                    
                    # Save result
                    if controller.save_document(output_file):
                        print(f"✅ Success! Saved to: {output_file}")
                        
                        # Show final info
                        info = controller.get_document_info()
                        print(f"Final info: {info}")
                    else:
                        print("❌ Failed to save")
                else:
                    print("❌ Replacements failed")
            else:
                print("❌ Text extraction failed")
        else:
            print("❌ Failed to open document")
            
    finally:
        controller.disconnect()


if __name__ == "__main__":
    test_clipboard_controller()
