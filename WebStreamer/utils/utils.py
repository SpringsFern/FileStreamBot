import sys
import glob
import importlib
from pathlib import Path

ppath = "WebStreamer/bot/plugins/*.py"
files = glob.glob(ppath)

# https://github.com/EverythingSuckz/TG-FileStreamBot/blob/webui/WebStreamer/__main__.py
def load_plugins(path: str):
    print('--------------------------- Importing ---------------------------')
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"{path}/{plugin_name}.py")
            import_path = ".plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["WebStreamer.bot.plugins." + plugin_name] = load
            print("Imported => " + plugin_name)