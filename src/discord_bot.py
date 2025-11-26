"""Discord bot + HTTP bridge for TTS playback.

Endpoints:
- POST /speak { text, channel_id?, guild_id?, member_id? }

Slash commands:
- /join, /leave, /speak

Requirements: set `DISCORD_TOKEN` env var and have `ffmpeg` available in PATH.
"""
from dotenv import load_dotenv
from pathlib import Path
import os
import tempfile
import asyncio
import pyttsx3
from aiohttp import web
import discord
from discord import app_commands
import shutil
import platform
from gtts import gTTS
import logging

logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parents[1] / ".env"
# override=True força o .env a sobrescrever variáveis de ambiente existentes
load_dotenv(env_path, override=True)

TOKEN = os.getenv('DISCORD_TOKEN')
PORT = int(os.getenv('DISCORD_BOT_PORT', '5000'))

# TTS Configuration
# TTS_ENGINE: 'gtts' (default, Google TTS - best quality) or 'pyttsx3' (espeak-ng - offline)
TTS_ENGINE = os.getenv('TTS_ENGINE', 'gtts').lower()
# TTS_LANGUAGE: Language code for gTTS (e.g., 'pt', 'en', 'es') or voice ID for pyttsx3
TTS_LANGUAGE = os.getenv('TTS_LANGUAGE', 'pt')
# TTS_VOICE_ID: Specific voice ID for pyttsx3 (e.g., 'roa/pt-br' for Portuguese Brazil in espeak-ng)
TTS_VOICE_ID = os.getenv('TTS_VOICE_ID', 'roa/pt-br')

intents = discord.Intents.default()
intents.voice_states = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Check if ffmpeg is available
HAS_FFMPEG = shutil.which('ffmpeg') is not None

# TTS engine cache to avoid slow initialization
_tts_engine = None
_tts_warning_shown = False
_member_voice_cache = {}  # Cache: member_id -> voice_channel

# Server-specific TTS configuration (guild_id -> config dict)
_guild_tts_config = {}  # Format: {guild_id: {'engine': 'gtts', 'language': 'pt', 'voice_id': 'roa/pt-br'}}

def get_guild_config(guild_id):
    """Get TTS configuration for a specific guild."""
    if guild_id and guild_id in _guild_tts_config:
        return _guild_tts_config[guild_id]
    # Return global defaults
    return {
        'engine': TTS_ENGINE,
        'language': TTS_LANGUAGE,
        'voice_id': TTS_VOICE_ID
    }

def get_tts_engine(guild_id=None):
    """Get or create a cached TTS engine instance based on configuration.
    
    Returns None if using gTTS (Google TTS), otherwise returns pyttsx3 engine.
    """
    global _tts_engine, _tts_warning_shown
    
    config = get_guild_config(guild_id)
    engine_type = config['engine']
    
    # Check if user wants to force gTTS (Google TTS)
    if engine_type == 'gtts':
        if not _tts_warning_shown:
            logger.info(f"🎤 Using gTTS (Google Text-to-Speech) - Language: {TTS_LANGUAGE}")
            logger.info("   Configure with TTS_ENGINE=pyttsx3 to use espeak-ng instead")
            _tts_warning_shown = True
        return None  # None triggers gTTS usage in the calling code
    
    # Initialize pyttsx3 engine (espeak-ng on Linux, SAPI5 on Windows)
    if _tts_engine is None:
        if platform.system() == 'Windows':
            logger.info("🎤 Initializing TTS with SAPI5 (Windows native)")
            try:
                _tts_engine = pyttsx3.init(driverName='sapi5')
            except Exception as e:
                logger.error(f"Failed to initialize SAPI5: {e}")
                logger.info("Falling back to gTTS")
                return None
        else:
            try:
                logger.info("🎤 Initializing TTS with pyttsx3 (espeak-ng on Linux)")
                _tts_engine = pyttsx3.init()
            except Exception as e:
                if not _tts_warning_shown:
                    logger.warning(f"pyttsx3 init failed: {e}. Falling back to gTTS.")
                    _tts_warning_shown = True
                return None
        
        if _tts_engine:
            _tts_engine.setProperty('rate', 180)
            
            # List and configure voices
            try:
                voices = _tts_engine.getProperty('voices')
                logger.info(f"📢 Available pyttsx3 voices: {len(voices)}")
                
                # Try to set the configured voice
                target_voice_id = config.get('voice_id', TTS_VOICE_ID)
                target_voice = None
                for voice in voices:
                    voice_id_lower = voice.id.lower()
                    # Check if voice matches configured voice ID
                    if target_voice_id.lower() in voice_id_lower:
                        target_voice = voice.id
                        logger.info(f"  ✅ Found configured voice: {voice.name} (ID: {voice.id[:80]}...)")
                        break
                
                # If specific voice not found, list some options
                if not target_voice:
                    logger.warning(f"⚠️ Configured voice '{target_voice_id}' not found. Available voices:")
                    for i, voice in enumerate(voices[:10]):  # Show first 10
                        logger.info(f"    - {voice.name} (ID: {voice.id[:60]}...)")
                    if len(voices) > 10:
                        logger.info(f"    ... and {len(voices) - 10} more voices")
                    logger.info(f"   Use /config command to set a different voice")
                    target_voice = voices[0].id if voices else None
                
                # Set the voice
                if target_voice:
                    _tts_engine.setProperty('voice', target_voice)
                    logger.info(f"🔊 Using voice: {target_voice[:80]}...")
                    
            except Exception as e:
                logger.warning(f"Could not configure voices: {e}")
                
    return _tts_engine


# detect optional PyNaCl (required by discord.py for voice support)
try:
    import nacl  # type: ignore
    HAS_PYNACL = True
except Exception:
    HAS_PYNACL = False


async def find_voice_channel_for_member(member_id: int):
    """Search all guilds' voice channels for a member with the given id and return the channel."""
    # First check cache
    if member_id in _member_voice_cache:
        channel = _member_voice_cache[member_id]
        # Verify channel is still valid
        if channel and any(m.id == member_id for m in channel.members):
            return channel
        else:
            _member_voice_cache.pop(member_id, None)
    
    # Fallback to full search (happens on bot startup or cache miss)
    for g in client.guilds:
        for vc in g.voice_channels:
            for m in vc.members:
                if m.id == member_id:
                    _member_voice_cache[member_id] = vc  # Update cache
                    return vc
    return None


async def handle_speak(request):
    try:
        data = await request.json()
    except Exception:
        return web.Response(text='invalid json', status=400)

    text = data.get('text')
    channel_id = data.get('channel_id')
    guild_id = data.get('guild_id')
    member_id = data.get('member_id') or data.get('user_id')

    if not text:
        return web.Response(text='missing text', status=400)

    voice_channel = None

    # explicit channel
    if channel_id:
        try:
            ch = client.get_channel(int(channel_id))
            if isinstance(ch, discord.VoiceChannel):
                voice_channel = ch
        except Exception:
            voice_channel = None

    # member id
    if not voice_channel and member_id:
        try:
            mid = int(member_id)
        except Exception:
            mid = None
        if mid:
            voice_channel = await find_voice_channel_for_member(mid)

    # guild fallback
    if not voice_channel and guild_id:
        try:
            g = client.get_guild(int(guild_id))
        except Exception:
            g = None
        if g:
            for vc in g.voice_channels:
                if vc.guild.voice_client and vc.guild.voice_client.is_connected():
                    voice_channel = vc
                    break
            if not voice_channel and g.voice_channels:
                voice_channel = g.voice_channels[0]

    # any available
    if not voice_channel:
        for g in client.guilds:
            if g.voice_channels:
                voice_channel = g.voice_channels[0]
                break

    if not voice_channel:
        return web.Response(text='no voice channel found', status=400)

    loop = asyncio.get_running_loop()
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmpname = tmp.name
    tmp.close()

    def _save():
        try:
            guild_id = voice_channel.guild.id if voice_channel and voice_channel.guild else None
            config = get_guild_config(guild_id)
            engine = get_tts_engine(guild_id)
            if engine is None:
                # Using gTTS (Google TTS)
                tts = gTTS(text=text, lang=config['language'])
                tts.save(tmpname)
            else:
                # Using pyttsx3 (espeak-ng on Linux, SAPI5 on Windows)
                engine.save_to_file(text, tmpname)
                engine.runAndWait()
        except Exception as e:
            # Last fallback: always use gTTS
            logger.error(f'TTS error: {e}, falling back to gTTS')
            try:
                guild_id = voice_channel.guild.id if voice_channel and voice_channel.guild else None
                config = get_guild_config(guild_id)
                tts = gTTS(text=text, lang=config['language'])
                tts.save(tmpname)
            except Exception as e2:
                logger.error(f'gTTS error: {e2}')
                raise

    await loop.run_in_executor(None, _save)

    try:
        if not HAS_PYNACL:
            return web.Response(text='PyNaCl (pip install pynacl) is required for voice support', status=500)
        
        if not HAS_FFMPEG:
            return web.Response(text='FFmpeg is required for voice support but was not found in PATH', status=500)

        vc = voice_channel.guild.voice_client
        if not vc or not vc.is_connected():
            vc = await voice_channel.connect()

        if vc.is_playing():
            vc.stop()

        source = discord.FFmpegPCMAudio(tmpname)
        vc.play(source)

        while vc.is_playing():
            await asyncio.sleep(0.1)

        try:
            os.unlink(tmpname)
        except Exception:
            pass

    except Exception as e:
        try:
            os.unlink(tmpname)
        except Exception:
            pass
        return web.Response(text=f'play error: {e}', status=500)

    return web.Response(text='ok')


@client.event
async def on_voice_state_update(member, before, after):
    """Track member voice state changes to maintain cache."""
    if after.channel:
        _member_voice_cache[member.id] = after.channel
    else:
        _member_voice_cache.pop(member.id, None)


@client.event
async def on_ready():
    print(f'✅ Discord bot ready as {client.user}')
    print(f'   Connected to {len(client.guilds)} guild(s)')
    for guild in client.guilds:
        print(f'   - {guild.name} (ID: {guild.id})')
    print(f'   PyNaCl: {"✅ Available" if HAS_PYNACL else "❌ Missing"}')
    print(f'   FFmpeg: {"✅ Available" if HAS_FFMPEG else "❌ Missing"}')
    print(f'   TTS Engine: {TTS_ENGINE.upper()}')
    print(f'   TTS Language: {TTS_LANGUAGE}')
    if TTS_ENGINE == 'pyttsx3':
        print(f'   TTS Voice ID: {TTS_VOICE_ID}')
    try:
        await tree.sync()
        print('✅ Slash commands synced')
    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')


@tree.command(name='join', description='Make the bot join your voice channel')
async def join(interaction: discord.Interaction):
    member = interaction.user
    if not isinstance(member, discord.Member) and interaction.guild:
        member = interaction.guild.get_member(member.id)

    if not HAS_PYNACL:
        await interaction.response.send_message('PyNaCl is required for voice support. Install it with `pip install pynacl` in the project venv.', ephemeral=True)
        return

    if member and member.voice and member.voice.channel:
        channel = member.voice.channel
        await interaction.response.defer(ephemeral=True)
        try:
            if interaction.guild.voice_client and interaction.guild.voice_client.is_connected():
                await interaction.guild.voice_client.move_to(channel)
            else:
                await channel.connect()
            await interaction.followup.send('Joined your channel.', ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f'Could not join channel: {e}', ephemeral=True)
    else:
        await interaction.response.send_message('You are not connected to a voice channel.', ephemeral=True)


@tree.command(name='leave', description='Make the bot leave the voice channel')
async def leave(interaction: discord.Interaction):
    if interaction.guild and interaction.guild.voice_client and interaction.guild.voice_client.is_connected():
        try:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message('Disconnected.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error disconnecting: {e}', ephemeral=True)
    else:
        await interaction.response.send_message('I am not connected to a voice channel.', ephemeral=True)


@tree.command(name='speak', description='Make the bot speak the given text in voice channel')
@app_commands.describe(text='Text to speak')
async def speak(interaction: discord.Interaction, text: str):
    # Respond immediately to avoid timeout
    await interaction.response.defer(ephemeral=True, thinking=True)
    
    target_vc = None
    if interaction.guild and interaction.guild.voice_client and interaction.guild.voice_client.is_connected():
        target_vc = interaction.guild.voice_client
    else:
        member = interaction.user
        if not isinstance(member, discord.Member) and interaction.guild:
            member = interaction.guild.get_member(member.id)
        if member and member.voice and member.voice.channel:
            try:
                    if not HAS_PYNACL:
                        await interaction.followup.send('PyNaCl is required for voice support. Install it with `pip install pynacl` in the project venv.', ephemeral=True)
                        return
                    if not HAS_FFMPEG:
                        await interaction.followup.send('FFmpeg is required but not found in PATH.', ephemeral=True)
                        return
                    target_vc = await member.voice.channel.connect()
            except Exception as e:
                await interaction.followup.send(f'Could not join your channel: {e}', ephemeral=True)
                return

    if not target_vc:
        await interaction.followup.send('No voice channel available to speak in.', ephemeral=True)
        return

    loop = asyncio.get_running_loop()
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmpname = tmp.name
    tmp.close()

    def _save():
        try:
            guild_id = interaction.guild.id if interaction.guild else None
            config = get_guild_config(guild_id)
            engine = get_tts_engine(guild_id)
            if engine is None:
                # Using gTTS (Google TTS)
                tts = gTTS(text=text, lang=config['language'])
                tts.save(tmpname)
            else:
                # Using pyttsx3 (espeak-ng on Linux, SAPI5 on Windows)
                engine.save_to_file(text, tmpname)
                engine.runAndWait()
        except Exception as e:
            # Last fallback: always use gTTS
            logger.error(f'TTS error: {e}, falling back to gTTS')
            try:
                guild_id = interaction.guild.id if interaction.guild else None
                config = get_guild_config(guild_id)
                tts = gTTS(text=text, lang=config['language'])
                tts.save(tmpname)
            except Exception as e2:
                logger.error(f'gTTS error: {e2}')
                raise

    try:
        # Generate audio file
        await loop.run_in_executor(None, _save)
        
        # Play audio
        if target_vc.is_playing():
            target_vc.stop()
        source = discord.FFmpegPCMAudio(tmpname)
        target_vc.play(source)
        
        # Wait for playback to finish
        while target_vc.is_playing():
            await asyncio.sleep(0.1)
        
        # Clean up
        try:
            os.unlink(tmpname)
        except Exception:
            pass
        
        await interaction.followup.send('✅ Spoke the text.', ephemeral=True)
    except Exception as e:
        try:
            os.unlink(tmpname)
        except Exception:
            pass
        await interaction.followup.send(f'❌ Error playing audio: {e}', ephemeral=True)


@tree.command(name='config', description='Configure TTS settings for this server (Admin only)')
@app_commands.describe(
    engine='TTS engine: gtts (Google TTS, best quality) or pyttsx3 (espeak-ng, offline)',
    language='Language code for gTTS (pt, en, es, fr, etc.) or leave empty',
    voice_id='Voice ID for pyttsx3/espeak-ng (e.g., roa/pt-br, en-us) or leave empty'
)
@app_commands.default_permissions(administrator=True)
async def config(
    interaction: discord.Interaction,
    engine: str = None,
    language: str = None,
    voice_id: str = None
):
    """Configure TTS settings for this server."""
    if not interaction.guild:
        await interaction.response.send_message('This command can only be used in a server.', ephemeral=True)
        return
    
    guild_id = interaction.guild.id
    
    # Get current config
    current_config = get_guild_config(guild_id)
    
    # If no parameters, show current config
    if engine is None and language is None and voice_id is None:
        embed = discord.Embed(
            title="🎤 TTS Configuration",
            description=f"Current settings for **{interaction.guild.name}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="Engine", value=current_config['engine'].upper(), inline=True)
        embed.add_field(name="Language", value=current_config['language'], inline=True)
        embed.add_field(name="Voice ID", value=current_config['voice_id'], inline=True)
        embed.add_field(
            name="How to change",
            value="Use `/config engine:gtts` or `/config engine:pyttsx3 voice_id:roa/pt-br`",
            inline=False
        )
        embed.add_field(
            name="Available Engines",
            value="• **gtts** - Google TTS (best quality, online)\n• **pyttsx3** - espeak-ng (offline, robotic)",
            inline=False
        )
        embed.add_field(
            name="Common Languages (gTTS)",
            value="• **pt** - Portuguese\n• **en** - English\n• **es** - Spanish\n• **fr** - French",
            inline=False
        )
        embed.add_field(
            name="Common Voice IDs (pyttsx3)",
            value="• **roa/pt-br** - Portuguese (Brazil)\n• **en-us** - English (US)\n• **roa/es** - Spanish",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Validate and update config
    new_config = current_config.copy()
    
    if engine is not None:
        engine = engine.lower()
        if engine not in ['gtts', 'pyttsx3']:
            await interaction.response.send_message(
                '❌ Invalid engine. Use `gtts` or `pyttsx3`.',
                ephemeral=True
            )
            return
        new_config['engine'] = engine
    
    if language is not None:
        new_config['language'] = language.lower()
    
    if voice_id is not None:
        new_config['voice_id'] = voice_id
    
    # Save config
    _guild_tts_config[guild_id] = new_config
    
    # Clear TTS engine cache to force reinitialization with new settings
    global _tts_engine, _tts_warning_shown
    _tts_engine = None
    _tts_warning_shown = False
    
    # Show success message
    embed = discord.Embed(
        title="✅ TTS Configuration Updated",
        description=f"New settings for **{interaction.guild.name}**",
        color=discord.Color.green()
    )
    embed.add_field(name="Engine", value=new_config['engine'].upper(), inline=True)
    embed.add_field(name="Language", value=new_config['language'], inline=True)
    embed.add_field(name="Voice ID", value=new_config['voice_id'], inline=True)
    embed.add_field(
        name="Note",
        value="Settings are temporary and will reset when the bot restarts. Use environment variables for permanent settings.",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def _start():
    app = web.Application()
    app.router.add_post('/speak', handle_speak)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', PORT)
    await site.start()
    await client.start(TOKEN)


def run_bot():
    if not TOKEN:
        print('DISCORD_TOKEN not set')
        return
    try:
        asyncio.run(_start())
    except KeyboardInterrupt:
        print('shutting down')
    except Exception as e:
        print('Error running bot:', e)


if __name__ == '__main__':
    run_bot()
