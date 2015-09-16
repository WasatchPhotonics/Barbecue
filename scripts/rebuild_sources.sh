#!/bin/bash
#
# run supporting pyuic, pyrcc files to generate resource files and qt
# designer conversions. Run this from the home project directory like:
# <project root> $ ./scripts/rebuild_sources.sh

pyuic4 \
    barbecue/ui/GainOffset.ui \
    -o barbecue/ui/GainOffset_layout.py

pyrcc4 \
    barbecue/ui/bbq_resources.qrc \
    -o barbecue/ui/bbq_resources_rc.py

