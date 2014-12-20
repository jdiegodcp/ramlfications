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

tree_light = (
    colored("==================================", "white") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "yellow") + "\n" +
    colored("==================================", "white") + "\n" +
    colored("Base URI: https://api.spotify.com/v1", "yellow") + "\n" +
    colored("|- /tracks", "green", attrs=["bold"]) + "\n" +
    colored("|  - /tracks/{id}", "green", attrs=["bold"]) + "\n" +
    colored("|- /users/{user_id}/playlists", "green", attrs=["bold"]) + "\n" +
    colored("|  - /users/{user_id}/playlists/{playlist_id}", "green", attrs=["bold"]) + "\n"
)

tree_dark = (
    colored("==================================", "grey") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "grey", attrs=["bold"]) + "\n" +
    colored("==================================", "grey") + "\n" +
    colored("Base URI: https://api.spotify.com/v1", "grey", attrs=["bold"]) + "\n" +
    colored("|- /tracks", "grey", attrs=["bold"]) + "\n" +
    colored("|  - /tracks/{id}", "grey", attrs=["bold"]) + "\n" +
    colored("|- /users/{user_id}/playlists", "grey", attrs=["bold"]) + "\n" +
    colored("|  - /users/{user_id}/playlists/{playlist_id}", "grey", attrs=["bold"]) + "\n"
)

tree_light_v = (
    colored("==================================", "white") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "yellow") + "\n" +
    colored("==================================", "white") + "\n" +
    colored("Base URI: https://api.spotify.com/v1", "yellow") + "\n" +
    colored("|- /tracks", "green", attrs=["bold"]) + "\n" +
    colored("|  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|  - /tracks/{id}", "green", attrs=["bold"]) + "\n" +
    colored("|    ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|- /users/{user_id}/playlists", "green", attrs=["bold"]) + "\n" +
    colored("|  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|  - /users/{user_id}/playlists/{playlist_id}", "green", attrs=["bold"]) + "\n" +
    colored("|    ⌙ PUT", "blue", attrs=["bold"]) + "\n"
)

tree_light_vv = (
    colored("==================================", "white") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "yellow") + "\n" +
    colored("==================================", "white") + "\n" +
    colored("Base URI: https://api.spotify.com/v1", "yellow") + "\n" +
    colored("|- /tracks", "green", attrs=["bold"]) + "\n" +
    colored("|  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|     Query Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|      ⌙ ids", "cyan", attrs=["bold"]) + "\n" +
    colored("|  - /tracks/{id}", "green", attrs=["bold"]) + "\n" +
    colored("|    ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|       URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|        ⌙ id", "cyan", attrs=["bold"]) + "\n" +
    colored("|- /users/{user_id}/playlists", "green", attrs=["bold"]) + "\n" +
    colored("|  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|     URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|      ⌙ user_id", "cyan", attrs=["bold"]) + "\n" +
    colored("|  - /users/{user_id}/playlists/{playlist_id}", "green", attrs=["bold"]) + "\n" +
    colored("|    ⌙ PUT", "blue", attrs=["bold"]) + "\n" +
    colored("|       URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|        ⌙ user_id", "cyan", attrs=["bold"]) + "\n" +
    colored("|       Form Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|        ⌙ name", "cyan", attrs=["bold"]) + "\n"
)

tree_light_vvv = (
    colored("==================================", "white") + "\n" +
    colored("Spotify Web API Demo - Simple Tree", "yellow") + "\n" +
    colored("==================================", "white") + "\n" +
    colored("Base URI: https://api.spotify.com/v1", "yellow") + "\n" +
    colored("|- /tracks", "green", attrs=["bold"]) + "\n" +
    colored("|  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|     Query Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|      ⌙ ids: Spotify Track IDs", "cyan", attrs=["bold"]) + "\n" +
    colored("|  - /tracks/{id}", "green", attrs=["bold"]) + "\n" +
    colored("|    ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|       URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|        ⌙ id: Spotify Track ID", "cyan", attrs=["bold"]) + "\n" +
    colored("|- /users/{user_id}/playlists", "green", attrs=["bold"]) + "\n" +
    colored("|  ⌙ GET", "blue", attrs=["bold"]) + "\n" +
    colored("|     URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|      ⌙ user_id: User ID", "cyan", attrs=["bold"]) + "\n" +
    colored("|  - /users/{user_id}/playlists/{playlist_id}", "green", attrs=["bold"]) + "\n" +
    colored("|    ⌙ PUT", "blue", attrs=["bold"]) + "\n" +
    colored("|       URI Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|        ⌙ user_id: User ID", "cyan", attrs=["bold"]) + "\n" +
    colored("|       Form Params", "cyan", attrs=["bold"]) + "\n" +
    colored("|        ⌙ name: Playlist Name", "cyan", attrs=["bold"]) + "\n"
)
