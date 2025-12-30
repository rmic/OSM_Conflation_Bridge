# About this project

## Why I built this
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

[← Back to the main page](index.md)