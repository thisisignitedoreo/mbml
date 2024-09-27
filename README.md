# MewnBase Mod-Loader
MewnBase Mod-Loader, that can install mods from shared repository, local mods,
and load many mods at a time.

## Quickstart
Download a nuitka build from the [latest release](https://github.com/thisisignitedoreo/mbml/releases/latest)
and run it, it is straightforward then.

## Mod file format
Mod file is a tar archive, that contains two files:
- `manifest.json`<br/>
  A manifest file that contains meta information about the mod, like name, authors,<br/>
  description and manifest version, that should be equal to zero.<br/>
  e.g. `{"name": "Mod name", "authors": ["author 1", "author 2"], "description": "A cool mod.\nDoes things like this.", "version": 0}`
- `mod.jar`<br/>
  A mod itself, packs only classes that should be replaced.<br/>
  e.g. An archive with one file: e.g. `com/cairn4/moonbase/desktop/DesktopLauncher.class`

To add your own mod to the game, press such button in the loader.

To add it to the [repo](https://github.com/thisisignitedoreo/mbml-repo), send a
pull request adding your mod to the index.json according to the previously
added mods and adding mod file itself.
