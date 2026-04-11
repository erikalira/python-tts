# Change Examples

Use these examples to choose a good starting point and target layer.

## Example: change a Discord slash command

Start with:

- `src/presentation/discord_commands.py`
- `src/presentation/discord_command_handlers.py`

Move into shared layers only if the change adds reusable flow logic or business
rules.

## Example: change HTTP input or response behavior

Start with:

- `src/presentation/http_controllers.py`
- `src/presentation/http_presenters.py`

If the change is about orchestration or policy, move it into `src/application/`.

## Example: change bot and desktop behavior together

Start with:

- `src/application/`
- `src/core/`

Avoid implementing the same rule twice in `src/presentation/` and `src/desktop/`.

## Example: change Desktop App hotkey behavior

Start with:

- `src/desktop/services/hotkey_services.py`
- `src/desktop/services/hotkey_capture.py`
- `src/desktop/app/tts_runtime.py`

If the change becomes a reusable flow decision, extract it into `src/application/`.

## Example: change Desktop App panel behavior

Start with:

- `src/desktop/gui/main_window.py`
- `src/desktop/gui/main_window_presenter.py`
- `src/desktop/app/desktop_actions.py`

Keep UI event wiring in desktop GUI/runtime modules and avoid pulling GUI
concerns into shared layers.

## Example: split a large file

Do it only if the split improves one of these:

- module responsibility
- contract clarity
- onboarding readability
- change isolation

Do not split only because a file is long.

## Example: introduce compatibility during a refactor

Allowed when it helps migrate safely.

Before leaving it in place, record:

- why it exists
- what the steady state is
- what will let you remove it
