---
layout: default
---

# Welcome to OSM Conflation Bridge

This tool bridges the gap between professional GIS analysis in **QGIS** and community mapping in **JOSM**. 


## 🚀 Features

- **Generic Mapping Engine:** Map any QGIS attribute to any OSM tag dynamically.
- **Dual-Tab Interface:** Separate "Setup" (configuration) from "Browser" (execution).
- **Live Geometry Sync:** Moving a feature in QGIS automatically updates the location and tags in JOSM.
- **Overpass Integration:** Automatically identifies existing OSM building IDs at your current location.
- **Persistent State:** Saves your filters, mappings, and progress automatically between sessions.
- **Smart Filtering:** Process large datasets by filtering specific attributes (e.g., specific provinces or status codes).

## 🛠 Installation

1. **Clone the Repository:**
   ```bash
   cd ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins
   git clone [https://github.com/rmic/osm-conflation-bridge.git](https://github.com/rmic/osm-conflation-bridge.git)
   ```

2. **Enable the Plugin:**
Open QGIS, go to `Plugins > Manage and Install Plugins`, and enable *OSM Conflation Bridge*.

Setup JOSM: Ensure JOSM is running and Remote Control is enabled in the settings (`Preferences > Remote Control > Enable remote control`

## 📖 How to Use

### 1. Configuration (Setup Tab)
- **Select Layer:** Choose the point layer you wish to conflate.
- **Apply Filters:** Define which features to process (e.g., `province_field` == `NAMUR`).
- **Map Tags:**
    - **Static:** Enter a fixed string (e.g., `emergency` = `ambulance_station`).
    - **Field:** Choose a QGIS column to map to an OSM key (e.g., `name` = `station_name`).
- **Apply:** Click **Apply Configuration** to build your processing queue and jump to the Browser tab.

### 2. Execution (Browser Tab)
- **Navigate:** Use **Next** and **Prev** to jump between features. QGIS will auto-zoom and highlight the current target.
- **Sync:**
    - **Manual:** Click the **⚡ Sync to JOSM** button.
    - **Automatic:** Use the QGIS Vertex Tool to move the point. The move will trigger an automatic update in JOSM.
- **JOSM Interaction:** The plugin will tell JOSM to download the area, select the building identified by Overpass, and prepare the tags for upload.

## ⚙️ Technical Requirements

- **QGIS** 3.x
- **JOSM** (with Remote Control enabled)
- **Python Libraries:** `requests`

## 🗺 Roadmap

- [ ] Add a context menu to auto-fill Field names in the tag table.
- [ ] Implement a "Status" indicator for Overpass API responses.
- [ ] Add support for Polygon-to-Polygon conflation.
- [ ] Visual "Checklist" to mark features as "Done" in the source database.

## 📄 License

Distributed under the MIT License.