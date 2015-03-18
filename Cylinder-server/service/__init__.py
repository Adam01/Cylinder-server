import sys

if sys.platform.startswith("win"):
    import winservice

    main = winservice.main
elif sys.platform == "linux":
    import linuxservice

    main = linuxservice.main
