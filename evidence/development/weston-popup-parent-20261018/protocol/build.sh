#!/usr/bin/env bash
set -euo pipefail
wayland-scanner client-header /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml xdg-shell-client-protocol.h
wayland-scanner private-code /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml xdg-shell-protocol.c
cc -std=c11 -Wall -Wextra -Werror client.c xdg-shell-protocol.c $(pkg-config --cflags --libs wayland-client) -o client
