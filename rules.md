--- simplified
Important rules to remember: Project name is Multi-Emulator Launcher 1.0

1. To avoid confusion, the file must include #this belongs in [dir]/ [filename] or goes in root /[filename] - Version: [number] of updates to file, Keep the existing file header comments. "X-Seti - $MONTH$DATE 2025 -" rest of the header information.

Example: 
# X-Seti - August14 2025 -  Multi-Emulator Launcher - Game Scanner
"""
Games Catalog Methods - Handles populating a games database, system defined by folder name.
"""

List all def functions in alphabetical order, and class sections, like for example:

##Methods list -
# _load_file
# _populate_table
# _setup_system_tab
# _setup_table_structure
# _validate_game_file

##class COLParser: -
#__init__
# def log
# _is_multi_model_archive

Each method gets its own #vers [number]. Increase the version number so we can keep track of method changes.

Example: 
def _validate_game_file(main_window, file_path): #vers 1

2. The header's file name [filename] must match the save file. Keep filenames simple and unchanged. Avoid using words like 
   "Enhanced", 
   "Fallback", 
   "Improved", 
   "Fixed", 
   "Fix", 
   "Patch", 
   "Patched",
   "Updated",
   "Integrated", 
   "Clean"
   
Anywhere in the file, filename, method or functions. This will avoid confusion and file function duplication. Each set of related functions has its file.

3. Shared functions go in methods/ 
Themes .json files go in themes/
Core important /single-use functions go in core/ 
Editors go in components/ 
and GUI-related functions go in gui/
App-System-Settings - theme engine goes in utils/
 
4. "CRITICAL: When fixing bugs, you must preserve 100% of the original functionality. Do not simplify. Also, check for the original file first before creating a fix or update.

5. No patch files, Check for duplicate functions and give a warning, suggest removal of duplicates, consolidate functions that can be shared and placed into the methods/ folder.

5. Keep the files under 90k. No patch files! - Lots of patch files can make it hard to find problems, each file with a simple name indicating its functions. 

6. On the "Continue" prompt,  only make edits to complete the script.

7. Keep all replies short and to the point, as we have limited data on our pay plan.

8. No Conflicts: Keep track of functions in the project files. No duplicate functions. Check existing files and functions first before creating newer functions. 

9.  No fallback code - Works or doesn't work - no middle ground

10. Always ask first before creating files, suggesting ideas, but let me decide.

11. Read the Changelog file. List of TODO and functions fixed.
