#define _GNU_SOURCE
#include <wayland-client.h>
#include "xdg-shell-client-protocol.h"
#include <errno.h>
#include <poll.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

static struct wl_display *display;
static struct wl_compositor *compositor;
static struct wl_shm *shm;
static struct xdg_wm_base *shell;

static int64_t now_ms(void) {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return (int64_t)t.tv_sec * 1000 + t.tv_nsec / 1000000;
}
static void done(void *data, struct wl_callback *callback, uint32_t serial) {
    (void)serial; *(bool *)data = true; wl_callback_destroy(callback);
}
static const struct wl_callback_listener callback_listener = { done };
static bool wait_done(bool *ready) {
    int64_t deadline = now_ms() + 5000;
    while (!*ready) {
        if (wl_display_dispatch_pending(display) < 0) return false;
        if (*ready) break;
        if (wl_display_flush(display) < 0 && errno != EAGAIN) return false;
        int remaining = deadline - now_ms();
        if (remaining <= 0) { fprintf(stderr, "event deadline exceeded\n"); return false; }
        struct pollfd p = { wl_display_get_fd(display), POLLIN, 0 };
        if (poll(&p, 1, remaining) <= 0) return false;
        if (wl_display_dispatch(display) < 0) return false;
    }
    return true;
}
static bool sync_server(void) {
    bool ready = false;
    struct wl_callback *callback = wl_display_sync(display);
    wl_callback_add_listener(callback, &callback_listener, &ready);
    return wait_done(&ready);
}
static void ping(void *data, struct xdg_wm_base *base, uint32_t serial) {
    (void)data; xdg_wm_base_pong(base, serial);
}
static const struct xdg_wm_base_listener shell_listener = { ping };
static void global(void *data, struct wl_registry *registry, uint32_t id,
                   const char *interface, uint32_t version) {
    (void)data; (void)version;
    if (!strcmp(interface, "wl_compositor"))
        compositor = wl_registry_bind(registry, id, &wl_compositor_interface, 4);
    if (!strcmp(interface, "wl_shm"))
        shm = wl_registry_bind(registry, id, &wl_shm_interface, 1);
    if (!strcmp(interface, "xdg_wm_base")) {
        shell = wl_registry_bind(registry, id, &xdg_wm_base_interface, 1);
        xdg_wm_base_add_listener(shell, &shell_listener, NULL);
    }
}
static void global_removed(void *data, struct wl_registry *registry, uint32_t id) {
    (void)data; (void)registry; (void)id;
}
static const struct wl_registry_listener registry_listener = { global, global_removed };
static void configured(void *data, struct xdg_surface *surface, uint32_t serial) {
    xdg_surface_ack_configure(surface, serial); *(bool *)data = true;
}
static const struct xdg_surface_listener surface_listener = { configured };
static void top_configure(void *data, struct xdg_toplevel *top, int32_t width,
                          int32_t height, struct wl_array *states) {
    (void)data; (void)top; (void)width; (void)height; (void)states;
}
static void top_close(void *data, struct xdg_toplevel *top) { (void)data; (void)top; }
static const struct xdg_toplevel_listener top_listener = {
    .configure = top_configure, .close = top_close
};
static void popup_configure(void *data, struct xdg_popup *popup, int32_t x,
                            int32_t y, int32_t width, int32_t height) {
    (void)data; (void)popup; (void)x; (void)y; (void)width; (void)height;
}
static void popup_done(void *data, struct xdg_popup *popup) { (void)data; (void)popup; }
static const struct xdg_popup_listener popup_listener = {
    .configure = popup_configure, .popup_done = popup_done
};
static struct wl_buffer *buffer(int size, uint32_t color) {
    int fd = memfd_create("avelino-popup-order", MFD_CLOEXEC);
    size_t bytes = size * size * sizeof(uint32_t);
    if (fd < 0 || ftruncate(fd, bytes)) return NULL;
    uint32_t *pixels = mmap(NULL, bytes, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (pixels == MAP_FAILED) return NULL;
    for (int i = 0; i < size * size; ++i) pixels[i] = color;
    struct wl_shm_pool *pool = wl_shm_create_pool(shm, fd, bytes);
    struct wl_buffer *result = wl_shm_pool_create_buffer(pool, 0, size, size,
                                                       size * 4, WL_SHM_FORMAT_XRGB8888);
    wl_shm_pool_destroy(pool); munmap(pixels, bytes); close(fd); return result;
}
static bool paint(struct wl_surface *surface, struct wl_buffer *pixels, int size) {
    bool ready = false;
    wl_callback_add_listener(wl_surface_frame(surface), &callback_listener, &ready);
    wl_surface_attach(surface, pixels, 0, 0);
    wl_surface_damage_buffer(surface, 0, 0, size, size);
    wl_surface_commit(surface);
    return wait_done(&ready);
}
int main(int argc, char **argv) {
    if (argc != 3) return 64;
    display = wl_display_connect(NULL);
    if (!display) return 1;
    wl_registry_add_listener(wl_display_get_registry(display), &registry_listener, NULL);
    if (!sync_server() || !compositor || !shm || !shell) return 2;
    struct wl_surface *parent = wl_compositor_create_surface(compositor);
    struct xdg_surface *parent_xdg = xdg_wm_base_get_xdg_surface(shell, parent);
    bool parent_configured = false;
    xdg_surface_add_listener(parent_xdg, &surface_listener, &parent_configured);
    struct xdg_toplevel *top = xdg_surface_get_toplevel(parent_xdg);
    xdg_toplevel_add_listener(top, &top_listener, NULL);
    xdg_toplevel_set_title(top, "Avelino popup parent-order regression");
    wl_surface_commit(parent);
    if (!wait_done(&parent_configured)) return 3;
    struct wl_buffer *blue = buffer(100, 0x1976d2), *red = buffer(20, 0xd32f2f);
    if (!blue || !red || !paint(parent, blue, 100)) return 4;
    fprintf(stderr, "parent mapped; creating uncommitted non-grabbing popup\n");
    struct wl_surface *child = wl_compositor_create_surface(compositor);
    struct xdg_surface *child_xdg = xdg_wm_base_get_xdg_surface(shell, child);
    bool child_configured = false;
    xdg_surface_add_listener(child_xdg, &surface_listener, &child_configured);
    struct xdg_positioner *positioner = xdg_wm_base_create_positioner(shell);
    xdg_positioner_set_size(positioner, 20, 20);
    xdg_positioner_set_anchor_rect(positioner, 10, 10, 1, 1);
    xdg_positioner_set_anchor(positioner, XDG_POSITIONER_ANCHOR_TOP_LEFT);
    xdg_positioner_set_gravity(positioner, XDG_POSITIONER_GRAVITY_BOTTOM_RIGHT);
    struct xdg_popup *popup = xdg_surface_get_popup(child_xdg, parent_xdg, positioner);
    xdg_popup_add_listener(popup, &popup_listener, NULL);
    if (!sync_server()) return 5;
    fprintf(stderr, "committing parent before popup's first surface commit\n");
    wl_surface_damage_buffer(parent, 0, 0, 100, 100); wl_surface_commit(parent);
    if (!sync_server()) return 6;
    fprintf(stderr, "parent commit survived; mapping popup\n");
    wl_surface_commit(child);
    if (!wait_done(&child_configured) || !paint(child, red, 20)) return 7;
    FILE *receipt = fopen(argv[1], "w"); if (!receipt) return 8;
    fputs("{\"accepted\":false,\"parentCommitsBeforeFirstPopupCommit\":1,\"popupConfigured\":true,\"popupFrame\":true}\n", receipt);
    fclose(receipt);
    int64_t deadline = now_ms() + 10000;
    while (access(argv[2], F_OK) && now_ms() < deadline) usleep(20000);
    if (access(argv[2], F_OK)) return 9;
    xdg_popup_destroy(popup); xdg_surface_destroy(child_xdg); wl_surface_destroy(child);
    xdg_toplevel_destroy(top); xdg_surface_destroy(parent_xdg); wl_surface_destroy(parent);
    wl_buffer_destroy(red); wl_buffer_destroy(blue);
    wl_display_flush(display); wl_display_disconnect(display);
    return 0;
}
