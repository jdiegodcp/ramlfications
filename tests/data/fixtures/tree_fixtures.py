#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function


from termcolor import colored
# NOTE: I know that these should be caps being constants but I'm
# not liking that for some reason for fixtures. Deal.

tree_no_color = ("""\
==================================
Spotify Web API Demo - Simple Tree
==================================
Base URI: https://api.spotify.com/v1
|- /tracks
|  - /tracks/{id}
|- /users/{user_id}/playlists
|  - /users/{user_id}/playlists/{playlist_id}
""")

# NOTE: Since I am having the pipe ("|") consistent throughout in terms
# of color, as well as setting its ANSI color separately from the rest
# of the string - even if they are the same color - tests need to have
# call `colored()` around the pipe separately.

tree_light = (
    colored("==================================", "white") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "yellow") + "\n" +
    colored("==================================", "white") + "\n" +
    colored("Base URI: https://api.spotify.com/v1", "yellow") + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("- /tracks", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  - /tracks/{id}", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("- /users/{user_id}/playlists", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  - /users/{user_id}/playlists/{playlist_id}", "green",
            attrs=["bold"]) + "\n"
)

tree_dark = (
    colored("==================================", "grey") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "grey",
            attrs=["bold"]) + "\n" +
    colored("==================================", "grey") + "\n" +
    colored("Base URI: https://api.spotify.com/v1",
            "grey", attrs=["bold"]) + "\n" +
    colored("|", "grey", attrs=["bold"]) +
    colored("- /tracks", "grey", attrs=["bold"]) + "\n" +
    colored("|", "grey", attrs=["bold"]) +
    colored("  - /tracks/{id}", "grey", attrs=["bold"]) + "\n" +
    colored("|", "grey", attrs=["bold"]) +
    colored("- /users/{user_id}/playlists", "grey", attrs=["bold"]) + "\n" +
    colored("|", "grey", attrs=["bold"]) +
    colored("  - /users/{user_id}/playlists/{playlist_id}", "grey",
            attrs=["bold"]) + "\n"
)

tree_light_v = (
    colored("==================================", "white") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "yellow") + "\n" +
    colored("==================================", "white") + "\n" +
    colored("Base URI: https://api.spotify.com/v1", "yellow") + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("- /tracks", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  - /tracks/{id}", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("    ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("- /users/{user_id}/playlists", "green",
            attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  - /users/{user_id}/playlists/{playlist_id}", "green",
            attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("    ⌙ PUT", "blue", attrs=["bold"]) + "\n"
)

tree_light_vv = (
    colored("==================================", "white") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "yellow") + "\n" +
    colored("==================================", "white") + "\n" +
    colored("Base URI: https://api.spotify.com/v1", "yellow") + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("- /tracks", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("     Query Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("      ⌙ ids", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  - /tracks/{id}", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("    ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("       URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("        ⌙ id", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("- /users/{user_id}/playlists", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("     URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("      ⌙ user_id", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  - /users/{user_id}/playlists/{playlist_id}", "green",
            attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("    ⌙ PUT", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("       URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("        ⌙ user_id", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("       Form Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("        ⌙ name", "cyan", attrs=["bold"]) + "\n"
)

tree_light_vvv = (
    colored("==================================", "white") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "yellow") + "\n" +
    colored("==================================", "white") + "\n" +
    colored("Base URI: https://api.spotify.com/v1", "yellow") + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("- /tracks", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("     Query Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("      ⌙ ids: Spotify Track IDs", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  - /tracks/{id}", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("    ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("       URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("        ⌙ id: Spotify Track ID", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("- /users/{user_id}/playlists", "green", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("     URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("      ⌙ user_id: User ID", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("  - /users/{user_id}/playlists/{playlist_id}", "green",
            attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("    ⌙ PUT", "blue", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("       URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("        ⌙ user_id: User ID", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("       Form Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|", "green", attrs=["bold"]) +
    colored("        ⌙ name: Playlist Name", "cyan", attrs=["bold"]) + "\n"
)
