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

To add it to the [repo](https://github.com/thisisignitedoreo/mbml-repo), send an
issue about adding your mod, and it will be checked and added to repo asap!

## Thanks!

- neoclar for inventing method of running multiple mods at the same time and explaining a whole bunch of stuff to me
- Everyone else in the [MewnBase discord server](https://discord.gg/mewnbase) for the support
- Steve @Cairn4 for making such a cool game!

