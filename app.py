#!/usr/bin/env python3
"""
ZIP File Modifier Script
Creates new files inside existing ZIP archives at specified paths.
"""

import zipfile
import os
import argparse
import tempfile
import subprocess
from pathlib import Path

def create_symlink_in_zip(zip_path, target_path, symlink_target, overwrite=False):
    """
    Create a symbolic link inside a ZIP archive at the specified path.
    
    Args:
        zip_path (str): Path to the ZIP file
        target_path (str): Path inside the ZIP where symlink should be created
        symlink_target (str): Target path that the symlink points to
        overwrite (bool): Whether to overwrite existing files
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(zip_path):
        print(f"Error: ZIP file '{zip_path}' does not exist")
        return False
    
    # Normalize the target path (use forward slashes for ZIP)
    target_path = target_path.replace('\\', '/')
    
    try:
        # Create a temporary copy of the ZIP
        temp_zip = zip_path + '.tmp'
        
        with zipfile.ZipFile(zip_path, 'r') as original_zip:
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                # Copy all existing files
                for item in original_zip.infolist():
                    # Skip if we're about to overwrite and overwrite is False
                    if item.filename == target_path and not overwrite:
                        print(f"File '{target_path}' already exists. Use --overwrite to replace it.")
                        os.remove(temp_zip)
                        return False
                    
                    # Copy existing file (unless we're overwriting it)
                    if item.filename != target_path:
                        data = original_zip.read(item.filename)
                        new_zip.writestr(item, data)
                
                # Create symlink entry
                # In ZIP files, symlinks are stored as regular files containing the target path
                # with special external attributes to indicate it's a symlink
                info = zipfile.ZipInfo(target_path)
                info.create_system = 3  # Unix
                info.external_attr = (0o120000 | 0o755) << 16  # S_IFLNK | permissions
                new_zip.writestr(info, symlink_target.encode('utf-8'))
        
        # Replace original with modified version
        os.replace(temp_zip, zip_path)
        print(f"Successfully created symlink '{target_path}' -> '{symlink_target}' in '{zip_path}'")
        return True
        
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid ZIP file")
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        return False

def create_file_in_zip(zip_path, target_path, file_content="", overwrite=False):
    """
    Create a file inside a ZIP archive at the specified path.
    
    Args:
        zip_path (str): Path to the ZIP file
        target_path (str): Path inside the ZIP where file should be created
        file_content (str): Content to write to the file
        overwrite (bool): Whether to overwrite existing files
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(zip_path):
        print(f"Error: ZIP file '{zip_path}' does not exist")
        return False
    
    # Normalize the target path (use forward slashes for ZIP)
    target_path = target_path.replace('\\', '/')
    
    try:
        # Create a temporary copy of the ZIP
        temp_zip = zip_path + '.tmp'
        
        with zipfile.ZipFile(zip_path, 'r') as original_zip:
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                # Copy all existing files
                for item in original_zip.infolist():
                    # Skip if we're about to overwrite and overwrite is False
                    if item.filename == target_path and not overwrite:
                        print(f"File '{target_path}' already exists. Use --overwrite to replace it.")
                        os.remove(temp_zip)
                        return False
                    
                    # Copy existing file (unless we're overwriting it)
                    if item.filename != target_path:
                        data = original_zip.read(item.filename)
                        new_zip.writestr(item, data)
                
                # Add the new file
                new_zip.writestr(target_path, file_content)
        
        # Replace original with modified version
        os.replace(temp_zip, zip_path)
        print(f"Successfully created '{target_path}' in '{zip_path}'")
        return True
        
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid ZIP file")
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        return False

def view_file_in_zip(zip_path, target_path):
    """View the content of a file inside a ZIP archive."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            if target_path not in zip_file.namelist():
                print(f"Error: File '{target_path}' not found in ZIP archive")
                return None
            
            content = zip_file.read(target_path).decode('utf-8', errors='replace')
            print(f"\n=== Content of '{target_path}' ===")
            print("-" * 50)
            print(content)
            print("-" * 50)
            return content
            
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid ZIP file")
    except UnicodeDecodeError:
        print(f"Error: File '{target_path}' contains binary data and cannot be displayed as text")
    except Exception as e:
        print(f"Error reading file: {str(e)}")
    
    return None

def edit_file_in_zip(zip_path, target_path, use_editor=True):
    """Edit a file inside a ZIP archive using an external editor or inline."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            if target_path not in zip_file.namelist():
                print(f"Error: File '{target_path}' not found in ZIP archive")
                return False
            
            # Read current content
            current_content = zip_file.read(target_path).decode('utf-8', errors='replace')
        
        if use_editor:
            # Use external editor
            new_content = edit_with_external_editor(current_content, target_path)
            if new_content is None:
                print("Edit cancelled")
                return False
        else:
            # Inline editing mode
            print(f"\n=== Editing '{target_path}' ===")
            print("Current content:")
            print("-" * 30)
            print(current_content)
            print("-" * 30)
            print("\nEnter new content (press Ctrl+D or Ctrl+Z to finish):")
            
            content_lines = []
            try:
                while True:
                    line = input()
                    content_lines.append(line)
            except EOFError:
                pass
            
            new_content = '\n'.join(content_lines)
        
        # Update the file in ZIP
        return create_file_in_zip(zip_path, target_path, new_content, overwrite=True)
        
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid ZIP file")
    except UnicodeDecodeError:
        print(f"Error: File '{target_path}' contains binary data and cannot be edited as text")
    except Exception as e:
        print(f"Error editing file: {str(e)}")
    
    return False

def edit_with_external_editor(content, filename):
    """Open content in external editor and return modified content."""
    # Try to determine the best editor
    editors = [
        #os.environ.get('EDITOR'),
        'nano', 'vim', 'vi', 'code', 'subl', 'atom', 'gedit', 'notepad'
    ]
    
    editor = None
    for e in editors:
        if e and subprocess.run(['which', e], capture_output=True).returncode == 0:
            editor = e
            break
    
    if not editor:
        print("No suitable text editor found. Using inline mode.")
        return None
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix=f'_{Path(filename).name}', delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Open editor
        #result = subprocess.run([editor, tmp_path])
        result = subprocess.run(['nvim', tmp_path])
        
        if result.returncode == 0:
            # Read modified content
            with open(tmp_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"Editor exited with code {result.returncode}")
            return None
            
    finally:
        # Clean up temporary file
        os.unlink(tmp_path)

def is_symlink_in_zip(info):
    """Check if a ZipInfo entry represents a symbolic link."""
    # Check if external attributes indicate a symlink (Unix systems)
    return (info.create_system == 3 and 
            (info.external_attr >> 16) & 0o170000 == 0o120000)

def list_zip_contents(zip_path):
    """List all files and directories in the ZIP file."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            print(f"\nContents of '{zip_path}':")
            print("-" * 50)
            
            directories = set()
            files = []
            symlinks = []
            
            for info in zip_file.infolist():
                # Extract directory paths
                dir_path = '/'.join(info.filename.split('/')[:-1])
                if dir_path:
                    directories.add(dir_path + '/')
                
                # Collect file info
                if info.filename.endswith('/'):
                    print(f"📁 {info.filename}")
                elif is_symlink_in_zip(info):
                    # Read symlink target
                    target = zip_file.read(info.filename).decode('utf-8')
                    print(f"🔗 {info.filename} -> {target}")
                    symlinks.append(info.filename)
                else:
                    size_kb = info.file_size / 1024
                    print(f"📄 {info.filename} ({size_kb:.1f} KB)")
                    files.append(info.filename)
            
            print(f"\nAvailable directories for file creation:")
            for directory in sorted(directories):
                print(f"  📁 {directory}")
            
            print(f"\nFiles available for viewing/editing:")
            for file in sorted(files):
                print(f"  📄 {file}")
            
            if symlinks:
                print(f"\nSymbolic links:")
                for symlink in sorted(symlinks):
                    print(f"  🔗 {symlink}")
                
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid ZIP file")
    except FileNotFoundError:
        print(f"Error: ZIP file '{zip_path}' not found")

def interactive_mode():
    """Interactive mode for managing files in ZIP archives."""
    print("=== ZIP File Modifier - Interactive Mode ===\n")
    
    # Get ZIP file path
    while True:
        zip_path = input("Enter path to ZIP file: ").strip()
        if os.path.exists(zip_path):
            break
        print("File not found. Please enter a valid path.\n")
    
    while True:
        # List ZIP contents
        list_zip_contents(zip_path)
        
        print(f"\nChoose an action:")
        print("1. Create new file")
        print("2. View existing file")
        print("3. Edit existing file")
        print("4. Create symbolic link")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            # Create new file
            print(f"\nEnter the path inside the ZIP where you want to create the file.")
            print("Examples: media/newfile.txt, docs/readme.md, config/settings.json")
            
            target_path = input("\nTarget path: ").strip()
            if not target_path:
                continue
            
            print(f"\nEnter content for the file (press Ctrl+D or Ctrl+Z to finish):")
            content_lines = []
            try:
                while True:
                    line = input()
                    content_lines.append(line)
            except EOFError:
                pass
            
            file_content = '\n'.join(content_lines)
            overwrite = input(f"\nOverwrite if file exists? (y/N): ").lower().startswith('y')
            
            success = create_file_in_zip(zip_path, target_path, file_content, overwrite)
            if success:
                print(f"\n✅ File created successfully!")
            else:
                print(f"\n❌ Failed to create file.")
        
        elif choice == '2':
            # View existing file
            target_path = input("\nEnter file path to view: ").strip()
            if target_path:
                view_file_in_zip(zip_path, target_path)
        
        elif choice == '3':
            # Edit existing file
            target_path = input("\nEnter file path to edit: ").strip()
            if not target_path:
                continue
                
            use_editor = input("Use external editor? (Y/n): ").lower() != 'n'
            success = edit_file_in_zip(zip_path, target_path, use_editor)
            
            if success:
                print(f"\n✅ File edited successfully!")
            else:
                print(f"\n❌ Failed to edit file.")
        
        elif choice == '4':
            # Create symbolic link
            print(f"\nEnter the path inside the ZIP where you want to create the symlink.")
            print("Examples: media/link_to_passwd, docs/config_link, tmp/shortcut")
            
            target_path = input("\nSymlink path: ").strip()
            if not target_path:
                continue
            
            print(f"\nEnter the target path that the symlink should point to.")
            print("Examples: /etc/passwd, ../config/settings.json, /tmp/data")
            
            symlink_target = input("\nTarget path: ").strip()
            if not symlink_target:
                continue
            
            overwrite = input(f"\nOverwrite if file exists? (y/N): ").lower().startswith('y')
            
            success = create_symlink_in_zip(zip_path, target_path, symlink_target, overwrite)
            if success:
                print(f"\n✅ Symlink created successfully!")
            else:
                print(f"\n❌ Failed to create symlink.")
        
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")
        
        input("\nPress Enter to continue...")

def main():
    parser = argparse.ArgumentParser(
        description="Create, view, edit files and symlinks inside ZIP archives",
        epilog="""
Examples:
  # Create a new file
  %(prog)s archive.zip media/image.txt "Hello World"
  %(prog)s archive.zip docs/readme.md --file content.txt
  
  # View existing file
  %(prog)s archive.zip docs/existing.txt --view
  
  # Edit existing file
  %(prog)s archive.zip config/settings.json --edit
  %(prog)s archive.zip config/settings.json --edit --inline
  
  # Create symbolic link
  %(prog)s archive.zip media/link_to_passwd --symlink /etc/passwd
  %(prog)s archive.zip config/settings_link --symlink ../settings.json
  
  # List contents (shows files, dirs, and symlinks)
  %(prog)s archive.zip --list
  
  # Interactive mode
  %(prog)s --interactive
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('zip_file', nargs='?', help='Path to the ZIP file')
    parser.add_argument('target_path', nargs='?', help='Path inside ZIP where file/symlink should be created/viewed/edited')
    parser.add_argument('content', nargs='?', default='', help='Content for the new file (create mode only)')
    
    # File operations
    parser.add_argument('--file', '-f', help='Read content from file instead of argument')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    parser.add_argument('--view', '-v', action='store_true', help='View content of existing file')
    parser.add_argument('--edit', '-e', action='store_true', help='Edit existing file')
    parser.add_argument('--inline', action='store_true', help='Use inline editing instead of external editor')
    parser.add_argument('--symlink', '-s', help='Create symbolic link pointing to this target')
    
    # Modes
    parser.add_argument('--list', '-l', action='store_true', help='List ZIP contents only')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # List mode
    if args.list:
        if not args.zip_file:
            print("Error: ZIP file path required for --list")
            return
        list_zip_contents(args.zip_file)
        return
    
    # View mode
    if args.view:
        if not args.zip_file or not args.target_path:
            print("Error: ZIP file and target path are required for --view")
            return
        view_file_in_zip(args.zip_file, args.target_path)
        return
    
    # Edit mode
    if args.edit:
        if not args.zip_file or not args.target_path:
            print("Error: ZIP file and target path are required for --edit")
            return
        use_editor = not args.inline
        success = edit_file_in_zip(args.zip_file, args.target_path, use_editor)
        if success:
            print("✅ File edited successfully!")
        else:
            print("❌ Failed to edit file.")
        return
    
    # Symlink mode
    if args.symlink:
        if not args.zip_file or not args.target_path:
            print("Error: ZIP file and target path are required for --symlink")
            return
        success = create_symlink_in_zip(args.zip_file, args.target_path, args.symlink, args.overwrite)
        if success:
            print("✅ Symlink created successfully!")
        else:
            print("❌ Failed to create symlink.")
        return
    
    # Create mode (default)
    if not args.zip_file or not args.target_path:
        print("Error: ZIP file and target path are required")
        parser.print_help()
        return
    
    # Read content from file if specified
    content = args.content
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}")
            return
    
    # Create the file in ZIP
    success = create_file_in_zip(args.zip_file, args.target_path, content, args.overwrite)
    if success:
        print("✅ File created successfully!")
    else:
        print("❌ Failed to create file.")

if __name__ == '__main__':
    main()
