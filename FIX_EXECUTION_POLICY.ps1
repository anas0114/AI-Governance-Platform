# Windows PowerShell Execution Policy Fix

# If you get this error when running .ps1 scripts:
# "Cannot be loaded because running scripts is disabled on this system"

# Run this command ONCE in PowerShell (as regular user, not admin):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then confirm by typing 'Y' and pressing Enter

# After that, you should be able to run all .ps1 scripts
