#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB
from __future__ import absolute_import, division, print_function

# NOTE: I know that these should be caps being constants but I'm
# not liking that for some reason for fixtures. Deal.

tree_light = (
    "\033[1;37m==================================\033[0m\n"
    "\033[1;33mSpotify Web API Demo - Simple Tree\033[0m\n"
    "\033[1;37m==================================\033[0m\n"
    "\033[1;33mBase URI: https://api.spotify.com/v1\033[0m\n"
    "\033[1;37m|\033[0m\033[1;32m- /tracks\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;32m- /tracks/{id}\033[0m\n"
    "\033[1;37m|\033[0m\033[1;32m- /users/{user_id}/playlists"
    "\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;32m- /users/{user_id}/playlists/"
    "{playlist_id}\033[0m\n"
)

tree_dark = (
    "\033[30m==================================\033[0m\n"
    "\033[1;30mSpotify Web API Demo - Simple Tree\033[0m\n"
    "\033[30m==================================\033[0m\n"
    "\033[1;30mBase URI: https://api.spotify.com/v1\033[0m\n"
    "\033[30m|\033[0m\033[1;30m- /tracks\033[0m\n"
    "\033[30m|\033[0m  \033[1;30m- /tracks/{id}\033[0m\n"
    "\033[30m|\033[0m\033[1;30m- /users/{user_id}/playlists\033[0m\n"
    "\033[30m|\033[0m  \033[1;30m- /users/{user_id}/playlists/"
    "{playlist_id}\033[0m\n"
)

tree_light_v = (
    "\033[1;37m==================================\033[0m\n"
    "\033[1;33mSpotify Web API Demo - Simple Tree\033[0m\n"
    "\033[1;37m==================================\033[0m\n"
    "\033[1;33mBase URI: https://api.spotify.com/v1\033[0m\n"
    "\033[1;37m|\033[0m\033[1;32m- /tracks\033[0m\n"
    "\033[1;37m|\033[0m\033[1;33m  ⌙ GET\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;32m- /tracks/{id}\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;33m  ⌙ GET\033[0m\n"
    "\033[1;37m|\033[0m\033[1;32m- /users/{user_id}/playlists"
    "\033[0m\n"
    "\033[1;37m|\033[0m\033[1;33m  ⌙ GET\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;32m- /users/{user_id}/playlists/"
    "{playlist_id}\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;33m  ⌙ PUT\033[0m\n"
)

tree_light_vv = (
    "\033[1;37m==================================\033[0m\n"
    "\033[1;33mSpotify Web API Demo - Simple Tree\033[0m\n"
    "\033[1;37m==================================\033[0m\n"
    "\033[1;33mBase URI: https://api.spotify.com/v1\033[0m\n"
    "\033[1;37m|\033[0m\033[1;32m- /tracks\033[0m\n"
    "\033[1;37m|\033[0m\033[1;33m  ⌙ GET\033[0m\n"
    "\033[1;37m|\033[0m     \033[1;36mQuery Params\033[0m\n"
    "\033[1;37m|\033[0m      ⌙ \033[1;36mids\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;32m- /tracks/{id}\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;33m  ⌙ GET\033[0m\n"
    "\033[1;37m|\033[0m       \033[1;36mURI Params\033[0m\n"
    "\033[1;37m|\033[0m        ⌙ \033[1;36mid"
    "\033[0m\n"
    "\033[1;37m|\033[0m\033[1;32m- /users/{user_id}/playlists"
    "\033[0m\n"
    "\033[1;37m|\033[0m\033[1;33m  ⌙ GET\033[0m\n"
    "\033[1;37m|\033[0m     \033[1;36mURI Params\033[0m\n"
    "\033[1;37m|\033[0m      ⌙ \033[1;36muser_id\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;32m- /users/{user_id}/playlists/"
    "{playlist_id}\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;33m  ⌙ PUT\033[0m\n"
    "\033[1;37m|\033[0m       \033[1;36mURI Params\033[0m\n"
    "\033[1;37m|\033[0m        ⌙ \033[1;36muser_id\033[0m\n"
    "\033[1;37m|\033[0m       \033[1;36mForm Params\033[0m\n"
    "\033[1;37m|\033[0m        ⌙ \033[1;36mname\033[0m\n"
)

tree_light_vvv = (
    "\033[1;37m==================================\033[0m\n"
    "\033[1;33mSpotify Web API Demo - Simple Tree\033[0m\n"
    "\033[1;37m==================================\033[0m\n"
    "\033[1;33mBase URI: https://api.spotify.com/v1\033[0m\n"
    "\033[1;37m|\033[0m\033[1;32m- /tracks\033[0m\n"
    "\033[1;37m|\033[0m\033[1;33m  ⌙ GET\033[0m\n"
    "\033[1;37m|\033[0m     \033[1;36mQuery Params\033[0m\n"
    "\033[1;37m|\033[0m      ⌙ \033[1;36mids: Spotify Track IDs"
    "\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;32m- /tracks/{id}\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;33m  ⌙ GET\033[0m\n"
    "\033[1;37m|\033[0m       \033[1;36mURI Params\033[0m\n"
    "\033[1;37m|\033[0m        ⌙ \033[1;36mid: Spotify Track ID"
    "\033[0m\n"
    "\033[1;37m|\033[0m\033[1;32m- /users/{user_id}/playlists"
    "\033[0m\n"
    "\033[1;37m|\033[0m\033[1;33m  ⌙ GET\033[0m\n"
    "\033[1;37m|\033[0m     \033[1;36mURI Params\033[0m\n"
    "\033[1;37m|\033[0m      ⌙ \033[1;36muser_id: User ID\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;32m- /users/{user_id}/playlists/"
    "{playlist_id}\033[0m\n"
    "\033[1;37m|\033[0m  \033[1;33m  ⌙ PUT\033[0m\n"
    "\033[1;37m|\033[0m       \033[1;36mURI Params\033[0m\n"
    "\033[1;37m|\033[0m        ⌙ \033[1;36muser_id: User ID\033[0m\n"
    "\033[1;37m|\033[0m       \033[1;36mForm Params\033[0m\n"
    "\033[1;37m|\033[0m        ⌙ \033[1;36mname: Playlist Name"
    "\033[0m\n"
)
