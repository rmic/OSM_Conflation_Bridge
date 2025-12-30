---
layout: default
---

# Welcome to OSM Conflation Bridge

This plugin is a small tool designed to make it easier to move data from **QGIS** into **OpenStreetMap** via the **JOSM** editor.

### Why I built this
This project started when I set out to map every ambulance, fire, and police station in Belgium. I had official open data files with the locations, but I quickly realized that simply importing them wasn't enough. 

Many of the "official" coordinates were slightly offset from the actual buildings on the ground (likely because they were generated from addresses rather than actual footprints). To do the job right, I had to fix the locations in my data while simultaneously adding the correct tags to the buildings in OSM. 

I found myself stuck in a loop: 
1. Find a marker in QGIS.
2. Zoom in and pan.
3. Check the attributes.
4. Click the JOSM Remote button.
5. Switch to JOSM to find the building and add the tags.
6. Switch back to QGIS and repeat.

It was a lot of clicking, zooming, and switching windows, which made it easy to lose track or make mistakes. I decided to spend that time building this plugin to handle the repetitive parts for me.

### What it does
The goal of the plugin is to reduce the manual "back-and-forth" so you can focus on the data itself:

* **Simple Navigation:** "Next" and "Previous" buttons let you step through your points one by one. The map moves with you, so you don't have to zoom and pan manually.
* **Automatic Building Search:** When you select a point, the plugin uses a quick Overpass query to see if there is already a building at that location.
* **Tag Transfer:** It reads the attributes from your QGIS layer and prepares them as OSM tags. It then sends the building ID and the tags directly to JOSM.
* **Human Verification:** You still have the final say. JOSM opens with the tags ready, allowing you to double-check that everything looks right before confirming the change.

By automating the "bridge" between QGIS and JOSM, the process becomes much less of a chore.



## 🚀 Features

- **Generic Mapping Engine:** Map any QGIS attribute to any OSM tag dynamically.
- **Live Geometry Sync:** Moving a feature in QGIS automatically updates the location and tags in JOSM.
- **Overpass Integration:** Automatically identifies existing OSM building IDs at your current location.
- **Persistent State:** Saves your filters, mappings, and progress automatically between sessions.
- **Smart Filtering:** Process large datasets by filtering specific attributes 

## 🛠 Installation

1. **Clone the Repository:**

Until the plugin is accepted in the official repository, clone the repository in the plugins folder of your QGIS installation.
**Note** : If you are using a profile other than default, replace `default` in the paths below with your specific profile name. 

If you are not sure, you can check the exact path to your profile directly in QGIS by going to `Settings > User Profiles > Open Active Profile Folder`

### MacOS
   ```bash
   cd ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins
   git clone [https://github.com/rmic/osm-conflation-bridge.git](https://github.com/rmic/osm-conflation-bridge.git)
   ```
### Linux
    ```
    cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
    git clone https://github.com/rmic/osm-conflation-bridge.git
    ```
### Windows 

Open Command Prompt or Powershell and run 
    ```
    cd %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins
    git clone https://github.com/rmic/osm-conflation-bridge.git
    ```



2. **Enable the Plugin:**
After cloning the repository, the plugin must be activated within QGIS:

    1. *Restart QGIS* : QGIS scans the plugins folder only on startup.
    2. *Open Plugin Manager* : go to `Plugins > Manage and Install Plugins`
    3. *Locate the plugin* : Search for "OSM Conflation Bridge" in the "Installed" tab.
    4. *Activate* : Check the box next to the plugin name. The plugin will appear under the Vector menu.

3. **Setup JOSM**

Ensure JOSM is running and Remote Control is enabled in the settings (`Preferences > Remote Control > Enable remote control`)

## Quick Start

Before you begin, ensure **JOSM** is open and that **Remote Control** is enabled in its settings (*Preferences > Remote Control > Enable Remote Control*).

1. **Load your data:** Open the layer containing your points in QGIS.
2. **Open the Plugin:** Click the **OSM Conflation Bridge** icon in your toolbar to open the plugin panel.
3. **Configure Tags:** In the plugin panel, select your layer and map your QGIS fields to the corresponding OSM tags (for example, map a "Name" column to the `name` tag).
    - **Select Layer:** Choose the point layer you wish to conflate.
    - **Apply Filters:** If your dataset is large, you can narrow it down by defining some filters.
    - **Map Tags:**
        - **Static:** Enter a fixed string (e.g., `emergency` = `ambulance_station`).
        - **From a data field:** Choose a QGIS column to map to an OSM key (e.g., `name` = `station_name`).
4. **Start your session:** * Click **Next** to automatically zoom to the first point in your list.
   * The plugin will search for a building at that location. 
   * If a building is found, the ID will appear in the panel.
5. **Send to JOSM:** Click the **Send to JOSM** button. JOSM will automatically zoom to the building and prompt you to apply the pre-filled tags.
6. **Verify and Repeat:** Check the data in JOSM, confirm the tags, upload, and click **Next** in QGIS to move to the next data point.

## 📖 How to Use

### 1. Configuration (Setup Tab)

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

## 🗺 Roadmap

- [ ] Add a context menu to auto-fill Field names in the tag table.
- [ ] Add support for Polygon-to-Polygon conflation.
- [ ] Visual "Checklist" to mark features as "Done" in the source database.

## 📄 License

Distributed under the GPLv2 License.