# Copyright (c) 2025 rmic
# Licensed under the terms of GNU GPL v2

import os, json, requests
from qgis.utils import iface
from qgis.core import QgsWkbTypes, QgsProject, QgsMapLayerProxyModel, QgsFieldProxyModel, QgsApplication
from qgis.gui import QgsRubberBand, QgsMapLayerComboBox, QgsFieldComboBox
from PyQt5.QtCore import Qt, QUrl, QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QDockWidget, QTabWidget, 
                             QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QAction)

class ConflationBridgeDock(QDockWidget):
    def __init__(self, iface, parent=None):
        super().__init__("OSM Conflation Bridge", parent)
        self.iface = iface
        self.root = QWidget()
        self.layout = QVBoxLayout(self.root)
        self.tabs = QTabWidget()
        
        # --- TAB 1: SETUP ---
        self.setup_page = QWidget()
        self.setup_layout = QVBoxLayout(self.setup_page)
        
        # Layer Selection
        self.setup_layout.addWidget(QLabel("<b>1. Select Layer</b>"))
        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.setup_layout.addWidget(self.layer_combo)

        # Filter Setup
        self.setup_layout.addWidget(QLabel("<b>2. Filter (Field == Value)</b>"))
        filter_row = QHBoxLayout()
        self.filter_field_combo = QgsFieldComboBox()
        self.filter_value_input = QLineEdit()
        self.filter_value_input.setPlaceholderText("Value (e.g. NAMUR)")
        filter_row.addWidget(self.filter_field_combo)
        filter_row.addWidget(self.filter_value_input)
        self.setup_layout.addLayout(filter_row)

        # Tag Mapping Table
        self.setup_layout.addWidget(QLabel("<b>3. Tag Mappings</b>"))
        self.tag_table = QTableWidget(0, 3)
        self.tag_table.setHorizontalHeaderLabels(["OSM Key", "Type", "Value/Field"])
        self.setup_layout.addWidget(self.tag_table)
        
        btn_add_tag = QPushButton("+ Add Tag")
        btn_add_tag.clicked.connect(self.add_tag_row)
        self.setup_layout.addWidget(btn_add_tag)
        
        self.btn_apply = QPushButton("Apply Configuration & Refresh")
        self.btn_apply.setStyleSheet("background-color: #d5f5e3; font-weight: bold;")
        self.setup_layout.addWidget(self.btn_apply)
        
        # --- TAB 2: BROWSER ---
        self.browser_page = QWidget()
        self.browser_layout = QVBoxLayout(self.browser_page)
        self.display = QTextEdit()
        self.display.setReadOnly(True)
        self.stats_label = QLabel("Configure the bridge first.")
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Prev")
        self.btn_next = QPushButton("Next ▶")
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        
        self.browser_layout.addWidget(QLabel("<b>Feature Info:</b>"))
        self.browser_layout.addWidget(self.display)
        self.browser_layout.addWidget(self.stats_label)
        self.browser_layout.addLayout(nav_layout)

        self.tabs.addTab(self.setup_page, "Setup")
        self.tabs.addTab(self.browser_page, "Browser")
        self.layout.addWidget(self.tabs)
        self.setWidget(self.root)

        self.btn_sync = QPushButton("⚡ Sync to JOSM")
        self.btn_sync.setStyleSheet("background-color: #fcf3cf; font-weight: bold; height: 30px;")
        self.btn_sync.clicked.connect(self.manual_sync)
        self.browser_layout.insertWidget(3, self.btn_sync)

        # Logic Vars
        self.features = []
        self.index = 0
        self.layer = None
        self.highlight = QgsRubberBand(iface.mapCanvas(), QgsWkbTypes.PointGeometry)
        self.highlight.setColor(Qt.red)
        self.highlight.setIconSize(14)

        # Signals
        self.layer_combo.layerChanged.connect(self.on_layer_changed)
        self.btn_apply.clicked.connect(self.refresh_data)
        self.btn_next.clicked.connect(self.next_feature)
        self.btn_prev.clicked.connect(self.prev_feature)

        self.nam = QgsApplication.networkAccessManager()

    def add_tag_row(self):
        row = self.tag_table.rowCount()
        self.tag_table.insertRow(row)
        
        # Key column
        self.tag_table.setItem(row, 0, QTableWidgetItem("key"))
        
        # Type column (Static vs Field)
        type_combo = QComboBox()
        type_combo.addItems(["Static", "Field"])
        self.tag_table.setCellWidget(row, 1, type_combo)
        
        # Value column (will be updated based on type)
        self.tag_table.setItem(row, 2, QTableWidgetItem("value"))

    def on_layer_changed(self, layer):
        self.layer = layer
        if layer:
            self.filter_field_combo.setLayer(layer)
            # Potentially update existing "Field" selectors in the table here

    def refresh_data(self):
        """Builds the feature list based on UI filters"""
        if not self.layer: return
        
        field = self.filter_field_combo.currentField()
        val = self.filter_value_input.text().strip().upper()
        
        self.features = [
            f for f in self.layer.getFeatures() 
            if str(f[field]).upper() == val
        ]
        
        self.index = 0
        self.tabs.setCurrentIndex(1) # Flip to Browser tab
        
        try: self.layer.geometryChanged.disconnect()
        except: pass
        self.layer.geometryChanged.connect(self.sync_to_josm)
        
        self.update_view()
        
    def remove_tag_row(self):
        curr = self.tag_table.currentRow()
        if curr >= 0:
            self.tag_table.removeRow(curr)

    def manual_sync(self):
        """Triggered by the button"""
        if self.features:
            feat = self.features[self.index]
            self.sync_to_josm(feat.id(), feat.geometry())

    def update_view(self):
        """Updates QGIS UI only (No JOSM call here to save resources)"""
        if not self.features:
            self.display.setText("No features found matching the filter.")
            return
        
        feat = self.features[self.index]
        self.display.setHtml("".join([f"<b>{f.name()}:</b> {feat[f.name()]}<br>" for f in feat.fields()]))
        self.stats_label.setText(f"Feature {self.index + 1} of {len(self.features)}")
        
        # Highlight and Zoom in QGIS
        self.layer.selectByIds([feat.id()])
        self.iface.mapCanvas().zoomToSelected(self.layer)
        self.highlight.setToGeometry(feat.geometry(), self.layer)
        self.save_state()

    def sync_to_josm(self, fid, geom):
        """Logic for both Manual Button and Geometry Move"""
        # Ensure we are working with the correct feature
        # If triggered by a move, fid might be different, but we check index for tags
        feat = self.layer.getFeature(fid)
        tags = []
        
        for r in range(self.tag_table.rowCount()):
            try:
                k = self.tag_table.item(r, 0).text()
                t = self.tag_table.cellWidget(r, 1).currentText()
                v = self.tag_table.item(r, 2).text()
                
                val = v if t == "Static" else str(feat[v])
                tags.append(f"{k}={val}")
            except Exception as e:
                print(f"Tag Mapping Error: {e}")

        lat, lon = geom.asPoint().y(), geom.asPoint().x()
        self.highlight.setToGeometry(geom, self.layer)
        self.process_josm_call(lat, lon, "|".join(tags))

    def process_josm_call(self, lat, lon, tag_str):
        # Fetch Building ID via Overpass
        query = f'[out:json];way["building"](around:15,{lat},{lon});out ids;'
        osm_id = None
        try:
            r = requests.post("https://overpass-api.de/api/interpreter", data={'data': query}, timeout=3)
            elements = r.json().get('elements', [])
            if elements: osm_id = elements[0].get('id')
        except: pass

        # Load/Zoom/Select in JOSM
        base_url = "http://127.0.0.1:8111/load_and_zoom"
        params = {
            "left": lon - 0.001, "right": lon + 0.001,
            "top": lat + 0.001, "bottom": lat - 0.001,
            "addtags": tag_str
        }
        if osm_id: params["select"] = f"way{osm_id}"
        
        params_str = "&".join([f"{k}={v}" for k, v in params.items()])
        

        url = QUrl(f"{base_url}?{params_str}")
        
        request = QNetworkRequest(url)
        self.nam.get(request)
        

    def next_feature(self):
        if self.index < len(self.features)-1: self.index += 1; self.update_view()

    def prev_feature(self):
        if self.index > 0: self.index -= 1; self.update_view()

    def save_state(self):
        # Collect Tag Table Data
        tag_data = []
        for r in range(self.tag_table.rowCount()):
            tag_data.append({
                "key": self.tag_table.item(r, 0).text(),
                "type": self.tag_table.cellWidget(r, 1).currentText(),
                "val": self.tag_table.item(r, 2).text()
            })

        state = {
            "index": self.index,
            "layer_id": self.layer.id() if self.layer else None,
            "filter_field": self.filter_field_combo.currentField(),
            "filter_val": self.filter_value_input.text(),
            "tags": tag_data
        }
        
        with open(os.path.join(os.path.expanduser("~"), "osm_bridge_config.json"), 'w') as f:
            json.dump(state, f)

    def load_state(self):
        path = os.path.join(os.path.expanduser("~"), "osm_bridge_config.json")
        if not os.path.exists(path): return
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                
            # Restore Filter Info
            self.filter_value_input.setText(data.get("filter_val", ""))
            
            # Restore Tags Table
            self.tag_table.setRowCount(0)
            for tag in data.get("tags", []):
                self.add_tag_row()
                row = self.tag_table.rowCount() - 1
                self.tag_table.item(row, 0).setText(tag['key'])
                self.tag_table.cellWidget(row, 1).setCurrentText(tag['type'])
                self.tag_table.item(row, 2).setText(tag['val'])
                
            return data.get("index", 0)
        except:
            return 0


class ConflationBridgePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.dock = None

    def initGui(self):

        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')

        self.dock = ConflationBridgeDock(self.iface)
        
        self.action = QAction(
            QIcon(icon_path), 
            "Toggle OSM Conflation Bridge", 
            self.iface.mainWindow()
        )
        
        self.action.triggered.connect(self.toggle_dock)

        self.iface.addPluginToVectorMenu("OSM Conflation Bridge", self.action)
        self.iface.addVectorToolBarIcon(self.action)
        
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.hide()

    def toggle_dock(self):
        if self.dock.isVisible():
            self.dock.hide()
        else:
            self.dock.show()

    def unload(self):
        # This cleans up the sidebar when the plugin is disabled
        if self.dock:
            self.iface.removeDockWidget(self.dock)
        
        self.iface.removePluginVectorMenu("OSM Conflation Bridge", self.action)
        self.iface.removeToolBarIcon(self.action)
