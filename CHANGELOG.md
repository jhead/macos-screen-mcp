# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Initial project setup
- Basic project structure
- Dependencies configuration
- Window management module
- MCP server implementation
- Screenshot capture functionality
- Base64 encoding option for image responses
- Search by owner name option with search_in_owner parameter
- CORS support for MCP server
- Health check endpoint for MCP server
- External connection support (0.0.0.0 binding)
- Enhanced logging configuration
- Keyboard control functionality
  - Added KeyboardManager class for handling keyboard input
  - Added send_key tool for sending individual key presses with modifiers
  - Added type_text tool for typing sequences of text
  - Support for common keys and modifier keys (command, shift, control, option)

### Changed

- Renamed module from `mcp-window` to `macos-screen-mcp` to better reflect its functionality
- Updated all documentation and configuration files to use the new module name
- Enhanced window search to include application name (owner) in search criteria
- Improved window search to prioritize exact matches in owner field
- Fixed screenshot capture by using correct Quartz methods for image dimensions
- Fixed screenshot capture by using correct Quartz methods for data provider access
- Fixed screenshot capture to only capture the target window by using window bounds
- Fixed screenshot capture to handle Retina displays by using kCGWindowListOptionIncludingWindow
- Fixed screenshot capture color accuracy by properly handling BGRA to RGBA conversion
- Updated server configuration for MCP compatibility
- Added numpy and python-jose dependencies for enhanced functionality

### Fixed

- Fixed incomplete CORS middleware configuration by adding missing allow_headers parameter
- Fixed truncated logging message in capture_window_screenshot function
- Fixed uvicorn server configuration in **main**.py to include all necessary parameters
- Fixed MCP server initialization by using correct initialize() method instead of non-existent wait_for_initialization()
- Added proper error handling for initialization failures

## [1.0.0] - 2024-04-06

### Added

- Initial implementation of window screenshot capture functionality
- Window management and search capabilities
- Health check endpoint
- Logging system with file and console output
- MCP SDK integration for protocol compliance

### Changed

- Refactored server to implement MCP protocol using official SDK
- Updated API endpoints to follow MCP specifications
- Improved error handling and logging
- Standardized base64 encoding for image responses

### Fixed

- Window screenshot capture reliability
- Error handling for non-existent windows
- Base64 encoding consistency
