while true; do
  textual run --dev myning/main.py
  STATUS=$?
  if [ $STATUS == 123 ]; then # Exit status 123 means time travel
    echo "Going back in time..."
  elif [ $STATUS == 122 ]; then # Exit status 122 means the game was updated
    echo "Restarting..."
  else
    break
  fi
done
