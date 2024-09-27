
from PySide6 import (
    QtGui,
    QtWidgets,
    QtCore,
)
from ui import Ui_MainWindow
import sys, os, json, shutil
import tarfile, subprocess, requests

class MewnModLoader(QtWidgets.QMainWindow):
    manifest_version = 0

    def __init__(self):
        super(MewnModLoader, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        app.setStyle("fusion")

        palette = QtGui.QPalette()

        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtGui.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtGui.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtGui.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtGui.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtGui.Qt.red)
        palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.HighlightedText, QtGui.Qt.black)

        app.setPalette(palette)
        app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    
        self.config = self.read_config()
        if self.config["game_path"]: self.ui.game_path.setText(self.config["game_path"])

        self.ui.l_movedown.setIcon(QtGui.QIcon(":/assets/assets/arrow_down.svg"))
        self.ui.l_moveup.setIcon(QtGui.QIcon(":/assets/assets/arrow_up.svg"))

        self.load_mod_online(None, None)
        self.load_mod_local(None)

        self.repo = self.fetch_online_repository()
        self.load_online_mods()
        self.update_local_mods()

        self.selected_mod = None

        self.connect()

    def connect(self):
        self.ui.browse_path_button.clicked.connect(self.browse_path)
        self.ui.online_mods.itemClicked.connect(self.online_mod_selected)
        self.ui.o_install.clicked.connect(self.install_mod)
        self.ui.l_uninstall.clicked.connect(self.uninstall_mod)
        self.ui.local_mods.itemChanged.connect(self.flip_mod_enabled)
        self.ui.local_mods.itemClicked.connect(self.local_mod_selected)
        self.ui.run_button.clicked.connect(self.run_game)
        self.ui.l_moveup.clicked.connect(lambda: self.swap_queue(True))
        self.ui.l_movedown.clicked.connect(lambda: self.swap_queue(False))
        self.ui.l_modinstall.clicked.connect(self.install_mod_local)

    def read_config(self):
        config_path = os.path.join(config_folder, "mbml", "config.json")
        default_config = {"game_path": None, "mods": {}, "mod_queue": []}
        
        if not os.path.isdir(os.path.dirname(config_path)):
            os.mkdir(os.path.dirname(config_path))
        
        if os.path.isfile(config_path) and json.load(open(config_path)).keys() != default_config.keys():
            os.remove(config_path)
        
        if not os.path.isfile(config_path):
            json.dump(default_config, open(config_path, "w"))
        
        return json.load(open(config_path))

    def write_config(self):
        config_path = os.path.join(config_folder, "mbml", "config.json")
        
        json.dump(self.config, open(config_path, "w"))

    def browse_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select MewnBase Installation Folder")
        if not path: return
        if not os.path.isfile(os.path.join(path, "MewnBase.exe")):
            QtWidgets.QMessageBox.warning(None, "Warning", "Select a valid MewnBase installation")
            return

        self.config["game_path"] = path
        self.ui.game_path.setText(self.config["game_path"])
        self.write_config()
    
    def fetch_online_repository(self):
        index_url = "https://thisisignitedoreo.github.io/mbml-repo/"
        request = requests.get(index_url)
        if not request.ok:
            return {}
        return request.json()
        # return {"testing": {"name": "testing mod", "authors": ["eeh idk"], "description": "testing mod\nfor testing purposes", "link": "local:mod.mbm"}, "invalid": {"name": "invalid mod", "authors": ["eeh idk"], "description": "testing mod\nshould not work", "link": "local:invalidmod.mbm"}}

    def load_mod_online(self, slug, mod):
        if not mod:
            self.ui.o_modname.setText("No mod selected")
            self.ui.o_authors.setText("No authors")
            self.ui.o_description.setPlainText("Select a mod in the pane to the left")
            self.ui.o_install.setEnabled(False)
        else:
            self.ui.o_modname.setText(mod["name"])
            self.ui.o_authors.setText("by: " + ", ".join(mod["authors"]))
            self.ui.o_description.setPlainText(mod["description"])
            if slug in self.config["mods"]:
                self.ui.o_install.setText("Uninstall mod")
            else:
                self.ui.o_install.setText("Install mod")
            self.ui.o_install.setEnabled(True)

    def load_mod_local(self, mod):
        if not mod:
            self.ui.l_modname.setText("No mod selected")
            self.ui.l_authors.setText("No authors")
            self.ui.l_description.setPlainText("Install a mod in the \"Repo\" tab")
            self.ui.l_uninstall.setEnabled(False)
        else:
            self.ui.l_modname.setText(mod["name"])
            self.ui.l_authors.setText("by: " + ", ".join(mod["authors"]))
            self.ui.l_description.setPlainText(mod["description"])
            self.ui.l_uninstall.setEnabled(True)
    
    def load_online_mods(self):
        self.ui.online_mods.clear()
        for k, i in self.repo.items():
            item = QtWidgets.QListWidgetItem(i["name"])
            item.setData(QtCore.Qt.ItemDataRole.UserRole, k)
            self.ui.online_mods.addItem(item)
    
    def online_mod_selected(self, item):
        mod = item.data(QtCore.Qt.ItemDataRole.UserRole)
        self.load_mod_online(mod, self.repo[mod])
        self.selected_mod = mod
    
    def download_mod(self, link, path):
        if link.startswith("local:"):
            # TODO: remove this debug security-nightmare feature
            shutil.copy(link[6:], path)
        else:
            file = self.download_file(link, lambda x, y: (self.ui.main_pbar.setMaximum(y) or self.ui.main_pbar.setValue(x)))
            open(path, "wb").write(file)

    def download_file(self, url, callback=None):
        request = requests.get(url, stream=True)
        if not request.ok:
            return None

        length = request.headers.get('content-length')
        data = b""

        if length is None:
            data += request.content
        else:
            dl = 0
            length = int(length)
            for d in request.iter_content(chunk_size=65536):
                dl += len(d)
                data += d
                if callback: callback(dl, length)

        return data

    def update_local_mods(self):
        self.ui.local_mods.clear()
        for mod in self.config["mod_queue"]:
            k, i = mod, self.config["mods"][mod]
            item = QtWidgets.QListWidgetItem(i["name"])
            item.setData(QtCore.Qt.ItemDataRole.UserRole, k)
            item.setCheckState(QtCore.Qt.CheckState.Checked if i["enabled"] else QtCore.Qt.CheckState.Unchecked)
            self.ui.local_mods.addItem(item)
    
    def swap_queue(self, up):
        if len(self.ui.local_mods.selectedItems()) == 0: return
        if up and self.ui.local_mods.currentRow() != 0:
            index = self.ui.local_mods.currentRow()
            self.config["mod_queue"][self.ui.local_mods.currentRow()], self.config["mod_queue"][self.ui.local_mods.currentRow()-1] = \
                self.config["mod_queue"][self.ui.local_mods.currentRow()-1], self.config["mod_queue"][self.ui.local_mods.currentRow()]
            self.update_local_mods()
            self.ui.local_mods.setCurrentRow(index-1)
        if not up and self.ui.local_mods.currentRow() != len(self.config["mod_queue"])-1:
            index = self.ui.local_mods.currentRow()
            self.config["mod_queue"][self.ui.local_mods.currentRow()], self.config["mod_queue"][self.ui.local_mods.currentRow()+1] = \
                self.config["mod_queue"][self.ui.local_mods.currentRow()+1], self.config["mod_queue"][self.ui.local_mods.currentRow()]
            self.update_local_mods()
            self.ui.local_mods.setCurrentRow(index+1)
        self.write_config()
    
    def flip_mod_enabled(self, item):
        mod = item.data(QtCore.Qt.ItemDataRole.UserRole)
        self.config["mods"][mod]["enabled"] = not self.config["mods"][mod]["enabled"]
        self.write_config()
    
    def local_mod_selected(self, item):
        mod = item.data(QtCore.Qt.ItemDataRole.UserRole)
        mod = self.config["mods"][mod]
        self.load_mod_local(mod)
            
    def uninstall_mod(self):
        mod = self.ui.local_mods.selectedItems()[0].data(QtCore.Qt.ItemDataRole.UserRole)
        self.install_mod_custom(mod)
        self.load_mod_local(None)
            
    def install_mod(self):
        mod = self.selected_mod
        self.install_mod_custom(mod)

    def install_mod_local(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select an .mbm file", "", "MewnBase Mod (*.mbm)")
        if not path: return
        if not tarfile.is_tarfile(path):
            QtWidgets.QMessageBox.warning(None, "Warning", "Not a MewnBase Mod file")
            return

        if not os.path.isdir(os.path.join(config_folder, "mbml", "temp")):
            os.mkdir(os.path.join(config_folder, "mbml", "temp"))
        
        mod_slug = os.path.basename(path).rsplit(".", 1)[0]
        shutil.copy(path, os.path.join(config_folder, "mbml", "temp", mod_slug + ".mbm"))
        self.install_mod_custom(mod_slug)
    
    def install_mod_custom(self, mod):
        if not self.config["game_path"]:
            QtWidgets.QMessageBox.warning(None, "Warning", "Select a valid MewnBase installation first")
            return

        config_path = os.path.join(config_folder, "mbml")
        if mod not in self.config["mods"]:
            if not os.path.isdir(os.path.join(config_path, "temp")):
                os.mkdir(os.path.join(config_path, "temp"))

            if not os.path.isfile(os.path.join(config_path, "temp", f"{mod}.mbm")):
                self.download_mod(self.repo[mod]["link"], os.path.join(config_path, "temp", f"{mod}.mbm"))

            if not os.path.isdir(os.path.join(config_path, "mods")):
                os.mkdir(os.path.join(config_path, "mods"))

            if os.path.isdir(os.path.join(config_path, "mods", mod)):
                shutil.rmtree(os.path.join(config_path, "mods", mod))
            
            os.mkdir(os.path.join(config_path, "mods", mod))

            tar = tarfile.open(os.path.join(config_path, "temp", f"{mod}.mbm"), "r:")
            tar.extractall(os.path.join(config_path, "mods", mod))
            tar.close()

            manifest = json.load(open(os.path.join(config_path, "mods", mod, "manifest.json")))
            if manifest["version"] != self.manifest_version:
                QtWidgets.QMessageBox.warning(None, "Warning", "Invalid manifest version.\nPlease inform repository owner of it.")
                shutil.rmtree(os.path.join(config_path, "mods", mod))
                return

            self.config["mods"][mod] = {
                "name": self.repo[mod]["name"],
                "authors": self.repo[mod]["authors"],
                "description": self.repo[mod]["description"],
                "enabled": True,
            }
            self.config["mod_queue"].append(mod)
        else:
            self.config["mods"].pop(mod)
            self.config["mod_queue"].remove(mod)
            shutil.rmtree(os.path.join(config_path, "mods", mod))

        self.write_config()

        if mod in self.repo:
            self.load_mod_online(mod, self.repo[mod])

        self.update_local_mods()
            
    def run_game(self):
        if not self.config["game_path"]:
            QtWidgets.QMessageBox.warning(None, "Warning", "Select a valid MewnBase installation first")
            return

        config_path = os.path.join(config_folder, "mbml")

        if not shutil.which("java"):
            QtWidgets.QMessageBox.warning(None, "Warning", "You should install Java locally.")
            return

        mods = []
        for i in self.config["mod_queue"]:
            if self.config["mods"][i]["enabled"]:
                mods.append(os.path.join(config_path, "mods", i, "mod.jar"))

        mods = mods[::-1]
        mods.append(os.path.join(self.config["game_path"], "game", "desktop-1.0.jar"))

        subprocess.run(["java", "-cp", (";" if os.name == "nt" else ":").join(mods), "com.cairn4.moonbase.desktop.DesktopLauncher"], cwd=self.config["game_path"])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    if os.name == "nt": config_folder = os.getenv("localappdata")
    else:
        config_folder = os.path.join(os.getenv("HOME"), ".config")
        if not os.path.isdir(config_folder):
            os.mkdir(config_folder)

    window = MewnModLoader()
    window.show()

    app.exec()
    config_path = os.path.join(config_folder, "mbml")
    if os.path.isdir(os.path.join(config_path, "temp")): shutil.rmtree(os.path.join(config_path, "temp"))
