#!/usr/bin/env python3
#this belongs in apps/utils/debug_logger.py - Version: 1
# X-Seti - November27 2025 - Multi-Emulator Launcher - Debug Logger

"""
Debug Logger Utility
Centralized debug logging that respects AppSettings debug mode and levels
"""

##Methods list -
# debug
# error
# info
# init_logger
# verbose
# warning

class DebugLogger: #vers 1
    """Centralized debug logger with level filtering"""
    
    # Debug levels (lower number = higher priority)
    LEVELS = {
        'ERROR': 0,
        'WARNING': 1,
        'INFO': 2,
        'DEBUG': 3,
        'VERBOSE': 4
    }
    
    def __init__(self, app_settings=None): #vers 1
        """Initialize debug logger
        
        Args:
            app_settings: AppSettings instance to read debug settings from
        """
        self.app_settings = app_settings
        self.enabled = False
        self.level = 'INFO'
        self.categories = set()
        
        if app_settings:
            self._load_settings()
    
    def _load_settings(self): #vers 2
        """Load debug settings from AppSettings"""
        if not self.app_settings:
            return

        settings = self.app_settings.current_settings
        self.enabled = settings.get('debug_mode', False)
        self.level = settings.get('debug_level', 'INFO')

        # Load enabled categories - handle both list and dict formats
        categories = settings.get('debug_categories', [])
        if isinstance(categories, dict):
            self.categories = {cat for cat, enabled in categories.items() if enabled}
        elif isinstance(categories, list):
            self.categories = set(categories)
        else:
            self.categories = set()
    
    def _should_log(self, level, category=None): #vers 1
        """Check if message should be logged
        
        Args:
            level: Message level (ERROR, WARNING, INFO, DEBUG, VERBOSE)
            category: Optional category filter
            
        Returns:
            True if message should be logged
        """
        # Always log errors regardless of debug mode
        if level == 'ERROR':
            return True
        
        # Check if debug mode enabled
        if not self.enabled:
            return False
        
        # Check level threshold
        current_level_value = self.LEVELS.get(self.level, 2)
        message_level_value = self.LEVELS.get(level, 2)
        
        if message_level_value > current_level_value:
            return False
        
        # Check category filter (if categories specified)
        if self.categories and category and category not in self.categories:
            return False
        
        return True
    
    def error(self, message, category=None): #vers 1
        """Log error message (always shown)"""
        if self._should_log('ERROR', category):
            prefix = f"[{category}] " if category else ""
            print(f"❌ ERROR: {prefix}{message}")
    
    def warning(self, message, category=None): #vers 1
        """Log warning message"""
        if self._should_log('WARNING', category):
            prefix = f"[{category}] " if category else ""
            print(f"⚠️  WARNING: {prefix}{message}")
    
    def info(self, message, category=None): #vers 1
        """Log info message"""
        if self._should_log('INFO', category):
            prefix = f"[{category}] " if category else ""
            print(f"ℹ️  INFO: {prefix}{message}")
    
    def debug(self, message, category=None): #vers 1
        """Log debug message"""
        if self._should_log('DEBUG', category):
            prefix = f"[{category}] " if category else ""
            print(f"🐛 DEBUG: {prefix}{message}")
    
    def verbose(self, message, category=None): #vers 1
        """Log verbose message (most detailed)"""
        if self._should_log('VERBOSE', category):
            prefix = f"[{category}] " if category else ""
            print(f"📝 VERBOSE: {prefix}{message}")


# Global logger instance
_logger = None

def init_logger(app_settings=None): #vers 1
    """Initialize global debug logger
    
    Args:
        app_settings: AppSettings instance
    """
    global _logger
    _logger = DebugLogger(app_settings)
    return _logger

def debug(message, category=None): #vers 1
    """Log debug message using global logger"""
    if _logger:
        _logger.debug(message, category)

def info(message, category=None): #vers 1
    """Log info message using global logger"""
    if _logger:
        _logger.info(message, category)

def warning(message, category=None): #vers 1
    """Log warning message using global logger"""
    if _logger:
        _logger.warning(message, category)

def error(message, category=None): #vers 1
    """Log error message using global logger"""
    if _logger:
        _logger.error(message, category)

def verbose(message, category=None): #vers 1
    """Log verbose message using global logger"""
    if _logger:
        _logger.verbose(message, category)
