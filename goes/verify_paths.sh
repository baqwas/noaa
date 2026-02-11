#!/usr/bin/env bash
echo -e "\n--- NOAA Path Verification ---\n"; for path in \
  "${HOME}/PycharmProjects/noaa/swpc/config.toml" \
  "${HOME}/PycharmProjects/noaa/goes/retrieve_goes.py" \
  "${HOME}/PycharmProjects/noaa/goes/retrieve_goes.sh" \
  "${HOME}/PycharmProjects/noaa/.venv/bin/activate" \
  "${HOME}/PycharmProjects/noaa/goes/logs"; \
do if [ -e "$path" ]; then echo -e "[\e[32m FOUND \e[0m] $path"; \
else echo -e "[\e[31m MISSING \e[0m] $path"; fi; done; echo -e "\n--- GOES Target Directories ---\n"; \
grep "dir =" "${HOME}/PycharmProjects/noaa/swpc/config.toml" | cut -d'"' -f2 | \
while read -r dir; do if [ -d "$dir" ]; then echo -e "[\e[32m FOUND \e[0m] Target Dir: $dir"; \
else echo -e "[\e[31m MISSING \e[0m] Target Dir: $dir"; fi; done