# python-bizneo

### bizneo.py
Still under hacking-developing phase. Look for `TOKEN_PARAMETER` and add your bizneo token there.

### bizneo_browser.py
Quick hack for now (still not headless). For supporting google login, we are using always the same Firefox profile, so you need to set `PROFILE_PATH` with one of your firefox profiles and manually login into bizneo. Consider using `time.sleep(100000)` or adding a `breakpoint()` for that initial manual requirement.
