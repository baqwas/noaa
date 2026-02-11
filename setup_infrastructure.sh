#!/bin/bash
# ==============================================================================
# NAME          : setup_infrastructure.sh
# DESCRIPTION   : Initializes the standardized directory tree for the 
#                 BeUlta Satellite & Weather Suite. Ensures audit compliance.
#
# AUTHOR        : Matha Goram
# VERSION       : 1.0.0
# UPDATED       : 2026-02-10
# LICENSE       : MIT License
#
# COPYRIGHT     : Copyright (c) 2026 ParkCircus Productions
#
# PROCESS FLOW:
#   1. Sets global path variables for data storage and project source.
#   2. Defines a Module Map containing all satellite instruments/categories.
#   3. Iterates through the map to build /images, /videos, and /logs folders.
#   4. Applies standard 755 permissions to the initialized tree.
#
# INTERFACE:
#   - Execution: ./setup_infrastructure.sh
#   - Note: This is an idempotent script (safe to run multiple times).
# ==============================================================================

# MIT License Statement:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software")...

# Define the root storage path
BASE_DIR="/home/reza/Videos/satellite"
PROJ_DIR="/home/reza/PycharmProjects/noaa"

echo "🌌 Initializing BeUlta Infrastructure Farm..."

# 1. Create Project Source Directories
mkdir -p "${PROJ_DIR}/"{epic,goes,swpc,terran,weather}

# 2. Define the Module Map (Module:Sub-Category1,Sub-Category2)
MODULES=(
    "epic:global"
    "noaa:goes_east,goes_west,2024eclipse_shapefiles"
    "swpc:aurora/north,aurora/south,solar_304,lasco_c3"
    "terran:land_use,ndvi_trends"
)

# 3. Build the Tree
for entry in "${MODULES[@]}"; do
    project="${entry%%:*}"
    sub_categories="${entry#*:}"
    
    # Convert comma-separated string to array
    IFS=',' read -ra ADDR <<< "$sub_categories"
    
    for sub in "${ADDR[@]}"; do
        echo "📂 Setting up: ${project}/${sub}"
        mkdir -p "${BASE_DIR}/${project}/${sub}/images"
        mkdir -p "${BASE_DIR}/${project}/${sub}/videos"
    done
    
    # Create centralized logs for each project
    mkdir -p "${BASE_DIR}/${project}/logs"
done

# 4. Final Permissions Check
chmod -R 755 "$BASE_DIR"

echo "---"
echo "✅ Infrastructure Setup Complete."
echo "🛡️ Run './swpc/system_audit.sh' to verify state: PASSED"

