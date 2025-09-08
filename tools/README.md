# MindBot Tools

This directory contains utility scripts for managing and maintaining MindBot.

## Available Tools

### Log Management (`manage_logs.py`)

A comprehensive log management tool for MindBot log files.

#### Usage
```bash
# List all log files
python tools/manage_logs.py list

# Show log statistics
python tools/manage_logs.py stats

# View recent log entries
python tools/manage_logs.py tail --lines 100

# Clean old logs (keep last 30 days)
python tools/manage_logs.py clean --days 30

# Compress log files to save space
python tools/manage_logs.py compress
```

#### Commands

- **`list`** - List all log files with size and modification time
- **`stats`** - Show comprehensive log statistics
- **`tail`** - Display recent log entries (default: 50 lines)
- **`clean`** - Remove log files older than specified days
- **`compress`** - Compress rotated log files to save disk space

#### Options

- **`--days N`** - Number of days to keep when cleaning (default: 30)
- **`--lines N`** - Number of lines to show when tailing (default: 50)

#### Examples

```bash
# Show last 200 lines of logs
python tools/manage_logs.py tail --lines 200

# Clean logs older than 7 days
python tools/manage_logs.py clean --days 7

# Get detailed statistics
python tools/manage_logs.py stats
```

## Log File Structure

MindBot stores logs in the `logs/` directory:

- `mindbot.log` - Main application log
- `mindbot.log.1`, `mindbot.log.2`, etc. - Rotated log files
- `mindbot.log.1.gz`, `mindbot.log.2.gz`, etc. - Compressed log files

## Log Rotation

Logs are automatically rotated when they reach the configured maximum size:

- **Default size**: 10MB
- **Backup count**: 5 files
- **Compression**: Optional (via compress command)

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure the script has write access to the logs directory
2. **File not found**: Check if the logs directory exists and contains log files
3. **Encoding errors**: Log files should be UTF-8 encoded

### Best Practices

1. **Regular cleanup**: Run `clean` command periodically to remove old logs
2. **Compression**: Use `compress` to save disk space on log files
3. **Monitoring**: Use `stats` to monitor log file growth
4. **Backup**: Consider backing up important log files before cleanup

## Integration

These tools are designed to work with:

- **Web Dashboard**: Log viewing via web interface
- **System Monitoring**: Integration with monitoring systems
- **Backup Systems**: Compatible with automated backup solutions
- **Log Aggregation**: Can be integrated with log aggregation tools

## Future Tools

Additional tools may be added to this directory:

- Configuration management tools
- Database maintenance scripts
- Performance monitoring utilities
- Backup and restore tools
