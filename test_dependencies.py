"""Test script to verify all dependencies are available."""
import sys
import shutil

def check_dependency(name, import_name=None, command_name=None):
    """Check if a dependency is available."""
    if import_name:
        try:
            __import__(import_name)
            print(f'✅ {name}: Available (Python package)')
            return True
        except ImportError:
            print(f'❌ {name}: Missing (Python package)')
            return False
    
    if command_name:
        if shutil.which(command_name):
            print(f'✅ {name}: Available (system command)')
            return True
        else:
            print(f'❌ {name}: Missing (system command)')
            return False
    
    return False

def main():
    """Check all required dependencies."""
    print('Checking dependencies...\n')
    
    all_ok = True
    
    # Python packages
    all_ok &= check_dependency('discord.py', 'discord')
    all_ok &= check_dependency('PyNaCl', 'nacl')
    all_ok &= check_dependency('pyttsx3', 'pyttsx3')
    all_ok &= check_dependency('Flask', 'flask')
    all_ok &= check_dependency('aiohttp', 'aiohttp')
    all_ok &= check_dependency('gunicorn', 'gunicorn')
    
    # System commands
    all_ok &= check_dependency('FFmpeg', command_name='ffmpeg')
    all_ok &= check_dependency('espeak-ng', command_name='espeak-ng')
    
    print('\n' + '='*50)
    if all_ok:
        print('✅ All dependencies are available!')
    else:
        print('❌ Some dependencies are missing!')
        sys.exit(1)

if __name__ == '__main__':
    main()
