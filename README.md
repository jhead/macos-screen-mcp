# macOS Screen View & Control MCP Server

A Model Context Protocol server that provides window screenshot capabilities. This server enables LLMs to capture screenshots of specific windows on macOS, either by window title or window ID.

### Available Tools

- `capture_window_screenshot` - Captures a screenshot of a specific window by its title or ID

  - `window_identifier` (string, required): Window title to search for or window ID
  - `search_in_owner` (boolean, optional): Whether to search in window owner names (default: true)
  - `format` (string, optional): Output format (binary or base64) (default: "binary")

- `list_windows` - Lists all visible windows

  - No parameters required

- `find_window` - Finds a window by title or owner name

  - `title` (string, required): Window title or owner name to search for
  - `search_in_owner` (boolean, optional): Whether to search in window owner names (default: true)

- `send_key` - Sends a keyboard key press event to the active window

  - `key` (string, required): The key to press (e.g., 'a', 'return', 'space')
  - `modifiers` (list of strings, optional): List of modifier keys to hold (e.g., ['command', 'shift'])

- `type_text` - Types a sequence of text characters
  - `text` (string, required): The text to type
  - `delay` (float, optional): Delay between keystrokes in seconds (default: 0.1)

### Supported Keys

The following keys are supported:

- Letters: a-z (case-insensitive)
- Numbers: 0-9
- Special keys: return, tab, space, delete, escape
- Arrow keys: up_arrow, down_arrow, left_arrow, right_arrow
- Modifier keys: command, shift, control, option (also right_shift, right_option, right_control)

### Examples

Send a single key press:

```python
await send_key("return")
```

Send a key with modifiers:

```python
await send_key("c", ["command"])  # Command+C (copy)
```

Type text:

```python
await type_text("Hello, World!")
```

## Installation

### Using pip

Install `macos_screen_mcp` via pip:

```bash
pip install git+ssh://git@github.com/jhead/macos-screen-mcp.git
```

After installation, you can run it as a script using:

```bash
python -m macos_screen_mcp
```

## Configuration

### Configure

Add to your Claude or Cursor settings:

```json
"mcpServers": {
 "macos-screen": {
    "name": "macos-screen",
    "url": "http://localhost:8000/sse",
    "description": "MCP server for capturing window screenshots",
    "version": "1.0.0"
  }
}
```

## Debugging

You can use the MCP inspector to debug the server:

```bash
npx @modelcontextprotocol/inspector python -m macos_screen_mcp
```

## Contributing

We encourage contributions to help expand and improve macos-screen-mcp. Whether you want to add new tools, enhance existing functionality, or improve documentation, your input is valuable.

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements to make macos-screen-mcp even more powerful and useful.

## License

macos-screen-mcp is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
