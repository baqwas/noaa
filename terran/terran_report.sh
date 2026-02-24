#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# 🌱 NAME          : terran_report.sh
# 📝 DESCRIPTION   : Sends an email summary of media and total storage used.
# 🔖 VERSION       : 1.2.0 (Disk Usage Integration)
# -------------------------------------------------------------------------------

DATE_STAMP=$(date +%Y-%m)
MEDIA_ROOT="/home/reza/Videos/satellite/terran"
SUMMARY_DIR="${MEDIA_ROOT}/monthly_summaries/${DATE_STAMP}"
RECIPIENT="reza@parkcircus.org"

# 1. Calculate Total Project Storage Usage
# 'du -sh' provides a human-readable total (e.g., 1.4G or 450M)
TOTAL_STORAGE=$(du -sh "$MEDIA_ROOT" | awk '{print $1}')

# 2. Check if the folder exists
if [ -d "$SUMMARY_DIR" ]; then
    FILE_LIST=$(ls -1 "$SUMMARY_DIR")

    # Compose the email
    (
      echo -e "Subject: 📊 [TERRAN-REPORT] Monthly Trends: ${DATE_STAMP}"
      echo -e "To: ${RECIPIENT}"
      echo -e "From: iot_admi@parkcircus.org"  # Updated to verified sender
      echo -e ""
      echo -e "Greetings,"
      echo "The following satellite trend media has been generated for your monitored counties:"
      echo ""
      echo "${FILE_LIST}"
      echo ""
      echo "-------------------------------------------------"
      echo "📊 STORAGE SUMMARY"
      echo "Total Disk Space Used: ${TOTAL_STORAGE}"
      echo "Location: ${MEDIA_ROOT}"
      echo "-------------------------------------------------"
      echo ""
      echo "End of automated report."
    ) | msmtp -a default "${RECIPIENT}"

    echo "✅ Monthly report (including storage metrics) sent to ${RECIPIENT}"
else
    echo "⚠️ No summary directory found for ${DATE_STAMP}. Skipping report."
fi