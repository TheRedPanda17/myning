#!/usr/bin/env python3

"""Script to invoke main to make imports work while dev'ing."""

from myning import main

try:
    main.main()
except KeyboardInterrupt:
    print("\nExited Myning. Thank you for playing!\n")
