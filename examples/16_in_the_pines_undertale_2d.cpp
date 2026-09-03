#include <windows.h>
#include <mmsystem.h>
#include <vector>
#include <string>
#include <cmath>
#include <cstdlib>
#include <algorithm>

using std::min;
using std::max;

#pragma comment(lib, "gdi32.lib")
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "winmm.lib")

// ==============================================================
// 1. CONSTANTS & COLOR PALETTE
// ==============================================================
const int INTERNAL_W = 640;
const int INTERNAL_H = 480;
uint32_t framebuffer[INTERNAL_W * INTERNAL_H];

// Color definitions (0x00RRGGBB)
const uint32_t C_BLACK        = 0x000000;
const uint32_t C_WHITE        = 0xFFFFFF;
const uint32_t C_SNOW_GROUND   = 0x0C121D;
const uint32_t C_PINE_DEEP    = 0x091B11;
const uint32_t C_PINE_MED     = 0x143522;
const uint32_t C_PINE_LIGHT   = 0x225436;
const uint32_t C_SNOW_WHITE   = 0xEDF2F7;
const uint32_t C_SNOW_BLUE    = 0xA0AEC0;
const uint32_t C_WOOD_SHADOW  = 0x24140D;
const uint32_t C_WOOD_LOG     = 0x442718;
const uint32_t C_WOOD_LIGHT   = 0x6B3E26;
const uint32_t C_ROOF_SHINGLE = 0x2D1B12;
const uint32_t C_SOUL_RED     = 0xFF0000;
const uint32_t C_LANTERN_AMBER= 0xF59E0B;
const uint32_t C_ICE_BLUE     = 0x38BDF8;
const uint32_t C_YELLOW_TEXT  = 0xFFFF00;
const uint32_t C_ORANGE_BTN   = 0xFF9900;
const uint32_t C_RAIL_TIE     = 0x332015;
const uint32_t C_RAIL_STEEL   = 0x64748B;
const uint32_t C_FIRE_ORANGE  = 0xEA580C;

// ==============================================================
// 2. PIXEL DRAWING PRIMITIVES & DYNAMIC LIGHTING
// ==============================================================
inline void put_pixel(int x, int y, uint32_t color) {
    if (x >= 0 && x < INTERNAL_W && y >= 0 && y < INTERNAL_H) {
        framebuffer[y * INTERNAL_W + x] = color;
    }
}

void clear_buffer(uint32_t color) {
    for (int i = 0; i < INTERNAL_W * INTERNAL_H; i++) framebuffer[i] = color;
}

void draw_rect(int rx, int ry, int rw, int rh, uint32_t color) {
    int x1 = max(0, rx);
    int y1 = max(0, ry);
    int x2 = min(INTERNAL_W, rx + rw);
    int y2 = min(INTERNAL_H, ry + rh);
    for (int y = y1; y < y2; y++) {
        for (int x = x1; x < x2; x++) {
            framebuffer[y * INTERNAL_W + x] = color;
        }
    }
}

void draw_rect_outline(int rx, int ry, int rw, int rh, int thick, uint32_t color) {
    draw_rect(rx, ry, rw, thick, color);
    draw_rect(rx, ry + rh - thick, rw, thick, color);
    draw_rect(rx, ry, thick, rh, color);
    draw_rect(rx + rw - thick, ry, thick, rh, color);
}

void draw_circle(int cx, int cy, int r, uint32_t color) {
    for (int dy = -r; dy <= r; dy++) {
        for (int dx = -r; dx <= r; dx++) {
            if (dx * dx + dy * dy <= r * r) {
                put_pixel(cx + dx, cy + dy, color);
            }
        }
    }
}

// Draw Soul Heart
void draw_soul_heart(int hx, int hy, uint32_t color) {
    const char* heart_map[10] = {
        "  ..    ..  ",
        " ....  .... ",
        "............",
        "............",
        "............",
        " .........  ",
        "  .......   ",
        "   .....    ",
        "    ...     ",
        "     .      "
    };
    for (int r = 0; r < 10; r++) {
        for (int c = 0; c < 12; c++) {
            if (heart_map[r][c] == '.') {
                put_pixel(hx + c - 6, hy + r - 5, color);
            }
        }
    }
}

// Rich Texturing: Gnarled Snowy Pine Tree
void draw_rich_pine_tree(int tx, int ty) {
    // Trunk
    draw_rect(tx + 22, ty + 60, 12, 28, C_WOOD_SHADOW);
    draw_rect(tx + 25, ty + 60, 6, 28, C_WOOD_LOG);

    // Bough 3 (Bottom)
    for (int y = 0; y < 28; y++) {
        int w = y * 2 + 10;
        draw_rect(tx + 28 - w / 2, ty + 42 + y, w, 1, C_PINE_DEEP);
    }
    // Snow Drift Layer 3
    draw_rect(tx + 4, ty + 56, 48, 5, C_SNOW_WHITE);
    draw_rect(tx + 8, ty + 54, 40, 2, C_SNOW_BLUE);

    // Bough 2 (Middle)
    for (int y = 0; y < 24; y++) {
        int w = y * 2 + 8;
        draw_rect(tx + 28 - w / 2, ty + 22 + y, w, 1, C_PINE_MED);
    }
    // Snow Drift Layer 2
    draw_rect(tx + 10, ty + 36, 36, 4, C_SNOW_WHITE);

    // Bough 1 (Top Crown)
    for (int y = 0; y < 22; y++) {
        int w = y * 2 + 4;
        draw_rect(tx + 28 - w / 2, ty + y, w, 1, C_PINE_LIGHT);
    }
    // Snow Cap
    draw_rect(tx + 22, ty + 6, 12, 4, C_SNOW_WHITE);
}

// Rich Texturing: Detailed Log Cabin
void draw_rich_cabin(int cx, int cy, bool has_lantern, int fire_anim) {
    // 1. Horizontal Cedar Logs with grooves
    for (int log = 0; log < 7; log++) {
        int ly = cy + 40 + log * 13;
        draw_rect(cx, ly, 160, 11, C_WOOD_LOG);
        draw_rect(cx, ly + 11, 160, 2, C_WOOD_SHADOW);     // Shadow between logs
        draw_rect(cx + 4, ly + 2, 152, 2, C_WOOD_LIGHT);   // Log highlight
    }

    // 2. Corner Notch Posts
    draw_rect(cx, cy + 38, 12, 94, C_WOOD_SHADOW);
    draw_rect(cx + 148, cy + 38, 12, 94, C_WOOD_SHADOW);

    // 3. Wooden Door with iron hinges
    draw_rect(cx + 66, cy + 82, 34, 50, 0x1A0F0A);
    draw_rect_outline(cx + 66, cy + 82, 34, 50, 2, C_WOOD_LIGHT);
    draw_rect(cx + 92, cy + 106, 4, 4, 0xD4D4D8); // Iron knob

    // 4. Overhanging Shingle Roof with deep snow drifts
    draw_rect(cx - 16, cy + 20, 192, 24, C_ROOF_SHINGLE);
    draw_rect(cx - 12, cy + 16, 184, 8, C_SNOW_WHITE); // Thick snow blanket
    draw_rect(cx - 8, cy + 22, 176, 3, C_SNOW_BLUE);

    // 5. Hearth Chimney with rising smoke puffs
    draw_rect(cx + 120, cy - 8, 20, 32, 0x374151);
    draw_rect(cx + 118, cy - 12, 24, 6, 0x1F2937);

    // 6. Glowing Window
    uint32_t win_glow = has_lantern ? C_LANTERN_AMBER : 0x1E293B;
    draw_rect(cx + 20, cy + 62, 32, 32, win_glow);
    draw_rect(cx + 34, cy + 62, 4, 32, C_WOOD_SHADOW); // Window frame cross
    draw_rect(cx + 20, cy + 76, 32, 4, C_WOOD_SHADOW);
}

// Wanderer Character Sprite (Kurt / Frisk)
void draw_rich_wanderer(int px, int py, int dir, int walk_frame) {
    int leg_offset = (walk_frame % 2 == 0) ? 0 : 3;

    // Acoustic Guitar strapped to back
    int gx = (dir == 1) ? (px + 16) : (px - 8);
    draw_rect(gx, py + 8, 10, 20, 0xD97706);     // Honey mahogany body
    draw_circle(gx + 5, py + 18, 3, 0x180E05);   // Soundhole
    draw_rect(gx + 3, py - 2, 4, 11, 0xFEF08A);  // Maple neck & tuning pegs

    // Parka Coat with highlights and shadow folds
    draw_rect(px, py + 10, 18, 18, 0x0369A1);
    draw_rect(px + 4, py + 12, 11, 15, 0x0284C7);

    // Warm Knitted Crimson Scarf
    draw_rect(px - 2, py + 8, 22, 5, 0xBE123C);
    draw_rect(px + 2, py + 13, 5, 8, 0x9F1239); // Hanging scarf tail

    // Face, Features & Messy Grunge Hair
    draw_rect(px + 3, py + 2, 12, 8, 0xFED7AA);
    draw_rect(px + 5, py + 5, 2, 2, 0x1E293B);   // Eye left
    draw_rect(px + 11, py + 5, 2, 2, 0x1E293B);  // Eye right

    // Blonde Grunge Hair Fringe
    draw_rect(px + 1, py - 3, 16, 6, 0xEAB308);
    draw_rect(px + 2, py + 1, 4, 5, 0xCA8A04);
    draw_rect(px + 12, py + 1, 4, 5, 0xCA8A04);

    // Winter Boots
    draw_rect(px + 2, py + 28, 5, 6 - leg_offset, 0x1E293B);
    draw_rect(px + 11, py + 28, 5, 6 + leg_offset, 0x1E293B);
}

// Monospace Font Bitmap
void draw_char(char c, int x, int y, uint32_t color, int scale = 2) {
    static const uint8_t font_data[95][7] = {
        {0x00,0x00,0x00,0x00,0x00,0x00,0x00}, // ' '
        {0x04,0x04,0x04,0x04,0x00,0x00,0x04}, // '!'
        {0x0A,0x0A,0x00,0x00,0x00,0x00,0x00}, // '"'
        {0x0A,0x1F,0x0A,0x0A,0x1F,0x0A,0x00}, // '#'
        {0x04,0x0F,0x14,0x0E,0x05,0x1E,0x04}, // '$'
        {0x18,0x19,0x02,0x04,0x08,0x13,0x03}, // '%'
        {0x08,0x14,0x14,0x08,0x15,0x12,0x0D}, // '&'
        {0x04,0x04,0x00,0x00,0x00,0x00,0x00}, // '\''
        {0x02,0x04,0x08,0x08,0x08,0x04,0x02}, // '('
        {0x08,0x04,0x02,0x02,0x02,0x04,0x08}, // ')'
        {0x00,0x0A,0x04,0x1F,0x04,0x0A,0x00}, // '*'
        {0x00,0x04,0x04,0x1F,0x04,0x04,0x00}, // '+'
        {0x00,0x00,0x00,0x00,0x00,0x04,0x08}, // ','
        {0x00,0x00,0x00,0x1F,0x00,0x00,0x00}, // '-'
        {0x00,0x00,0x00,0x00,0x00,0x04,0x04}, // '.'
        {0x01,0x02,0x04,0x08,0x10,0x00,0x00}, // '/'
        {0x0E,0x11,0x13,0x15,0x19,0x11,0x0E}, // '0'
        {0x04,0x0C,0x04,0x04,0x04,0x04,0x0E}, // '1'
        {0x0E,0x11,0x01,0x06,0x08,0x10,0x1F}, // '2'
        {0x1E,0x01,0x01,0x0E,0x01,0x01,0x1E}, // '3'
        {0x02,0x06,0x0A,0x12,0x1F,0x02,0x02}, // '4'
        {0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E}, // '5'
        {0x06,0x08,0x10,0x1E,0x11,0x11,0x0E}, // '6'
        {0x1F,0x01,0x02,0x04,0x08,0x08,0x08}, // '7'
        {0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E}, // '8'
        {0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C}, // '9'
        {0x00,0x04,0x04,0x00,0x04,0x04,0x00}, // ':'
        {0x00,0x04,0x04,0x00,0x04,0x08,0x00}, // ';'
        {0x02,0x04,0x08,0x10,0x08,0x04,0x02}, // '<'
        {0x00,0x1F,0x00,0x1F,0x00,0x00,0x00}, // '='
        {0x08,0x04,0x02,0x01,0x02,0x04,0x08}, // '>'
        {0x0E,0x11,0x01,0x06,0x04,0x00,0x04}, // '?'
        {0x0E,0x11,0x17,0x15,0x17,0x10,0x0F}, // '@'
        {0x0E,0x11,0x11,0x1F,0x11,0x11,0x11}, // 'A'
        {0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E}, // 'B'
        {0x0E,0x11,0x10,0x10,0x10,0x11,0x0E}, // 'C'
        {0x1C,0x12,0x11,0x11,0x11,0x12,0x1C}, // 'D'
        {0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F}, // 'E'
        {0x1F,0x10,0x10,0x1E,0x10,0x10,0x10}, // 'F'
        {0x0E,0x11,0x10,0x17,0x11,0x11,0x0F}, // 'G'
        {0x11,0x11,0x11,0x1F,0x11,0x11,0x11}, // 'H'
        {0x0E,0x04,0x04,0x04,0x04,0x04,0x0E}, // 'I'
        {0x07,0x02,0x02,0x02,0x02,0x12,0x0C}, // 'J'
        {0x11,0x12,0x14,0x18,0x14,0x12,0x11}, // 'K'
        {0x10,0x10,0x10,0x10,0x10,0x10,0x1F}, // 'L'
        {0x11,0x1B,0x15,0x15,0x11,0x11,0x11}, // 'M'
        {0x11,0x19,0x15,0x13,0x11,0x11,0x11}, // 'N'
        {0x0E,0x11,0x11,0x11,0x11,0x11,0x0E}, // 'O'
        {0x1E,0x11,0x11,0x1E,0x10,0x10,0x10}, // 'P'
        {0x0E,0x11,0x11,0x11,0x15,0x12,0x0D}, // 'Q'
        {0x1E,0x11,0x11,0x1E,0x14,0x12,0x11}, // 'R'
        {0x0E,0x11,0x10,0x0E,0x01,0x11,0x0E}, // 'S'
        {0x1F,0x04,0x04,0x04,0x04,0x04,0x04}, // 'T'
        {0x11,0x11,0x11,0x11,0x11,0x11,0x0E}, // 'U'
        {0x11,0x11,0x11,0x11,0x11,0x0A,0x04}, // 'V'
        {0x11,0x11,0x11,0x15,0x15,0x1B,0x11}, // 'W'
        {0x11,0x11,0x0A,0x04,0x0A,0x11,0x11}, // 'X'
        {0x11,0x11,0x0A,0x04,0x04,0x04,0x04}, // 'Y'
        {0x1F,0x01,0x02,0x04,0x08,0x10,0x1F}  // 'Z'
    };

    if (c >= 'a' && c <= 'z') c = c - 'a' + 'A';
    int idx = (c >= ' ' && c <= 'Z') ? (c - ' ') : 0;

    for (int row = 0; row < 7; row++) {
        uint8_t bits = font_data[idx][row];
        for (int col = 0; col < 5; col++) {
            if (bits & (1 << (4 - col))) {
                draw_rect(x + col * scale, y + row * scale, scale, scale, color);
            }
        }
    }
}

void draw_string(const std::string& str, int x, int y, uint32_t color, int scale = 2) {
    int cur_x = x;
    int cur_y = y;
    for (char c : str) {
        if (c == '\n') {
            cur_x = x;
            cur_y += 10 * scale;
            continue;
        }
        draw_char(c, cur_x, cur_y, color, scale);
        cur_x += 6 * scale;
    }
}

// ==============================================================
// 3. GAME STATE, INTERACTION & BATTLE
// ==============================================================
enum GameLocation { LOC_OUTSIDE, LOC_INSIDE_CABIN };
GameLocation g_loc = LOC_OUTSIDE;

enum GameState { STATE_OVERWORLD, STATE_BATTLE, STATE_DIALOG };
GameState g_state = STATE_OVERWORLD;

struct Player {
    float x = 320;
    float y = 340;
    int dir = 0;
    int walk_frame = 0;
    int walk_timer = 0;
    int hp = 20;
    bool has_lantern = false;
    bool has_hairpin = false;
    int clues = 0;
} g_player;

struct Footprint {
    int x, y;
    float life;
};
std::vector<Footprint> g_footprints;

struct Snowflake {
    float x, y, speed, size;
};
std::vector<Snowflake> g_snow;

struct BattleSystem {
    float soul_x = 320;
    float soul_y = 280;
    int box_x = 190;
    int box_y = 190;
    int box_w = 260;
    int box_h = 140;
    int selected_btn = 0;
    int turn = 0; // 0: Menu, 1: Attack, 2: Strum
    int turn_timer = 0;
    float timing_x = 0;
    bool enemy_pacified = false;
    int enemy_hp = 100;
    int shake = 0;
} g_battle;

struct Bullet {
    float x, y, vx, vy, r;
};
std::vector<Bullet> g_bullets;

// Active Dialogue System
bool g_dialog_open = false;
std::string g_dialog_line1 = "";
std::string g_dialog_line2 = "";
std::string g_interact_prompt = "";

// Fullscreen mode state
bool g_fullscreen = false;
RECT g_window_rect;

void toggle_fullscreen(HWND hwnd) {
    DWORD dwStyle = GetWindowLong(hwnd, GWL_STYLE);
    if (!g_fullscreen) {
        MONITORINFO mi = { sizeof(mi) };
        if (GetWindowPlacement(hwnd, (WINDOWPLACEMENT*)&g_window_rect) &&
            GetMonitorInfo(MonitorFromWindow(hwnd, MONITOR_DEFAULTTOPRIMARY), &mi)) {
            SetWindowLong(hwnd, GWL_STYLE, dwStyle & ~WS_OVERLAPPEDWINDOW);
            SetWindowPos(hwnd, HWND_TOP,
                mi.rcMonitor.left, mi.rcMonitor.top,
                mi.rcMonitor.right - mi.rcMonitor.left,
                mi.rcMonitor.bottom - mi.rcMonitor.top,
                SWP_NOOWNERZORDER | SWP_FRAMECHANGED);
            g_fullscreen = true;
        }
    } else {
        SetWindowLong(hwnd, GWL_STYLE, dwStyle | WS_OVERLAPPEDWINDOW);
        SetWindowPlacement(hwnd, (WINDOWPLACEMENT*)&g_window_rect);
        SetWindowPos(hwnd, NULL, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER |
            SWP_NOOWNERZORDER | SWP_FRAMECHANGED);
        g_fullscreen = false;
    }
}

// ==============================================================
// 4. OVERWORLD RENDERER
// ==============================================================
int g_fire_clock = 0;

void render_overworld() {
    clear_buffer(C_SNOW_GROUND);

    if (g_loc == LOC_OUTSIDE) {
        // Footprints
        for (const auto& fp : g_footprints) {
            draw_rect(fp.x, fp.y, 4, 3, 0x162132);
        }

        // Converging Cold Railroad Tracks on Right
        draw_rect(530, 0, 8, INTERNAL_H, C_RAIL_STEEL);
        draw_rect(570, 0, 8, INTERNAL_H, C_RAIL_STEEL);
        for (int y = 0; y < INTERNAL_H; y += 22) {
            draw_rect(520, y, 68, 5, C_RAIL_TIE);
        }

        // Giant Locomotive Drive Wheel
        draw_circle(554, 210, 28, 0x475569);
        draw_circle(554, 210, 16, 0x1E293B);
        draw_rect(550, 185, 8, 50, 0x94A3B8); // Balance bar

        // Pine Trees
        draw_rich_pine_tree(30, 30);
        draw_rich_pine_tree(120, 15);
        draw_rich_pine_tree(40, 260);
        draw_rich_pine_tree(110, 350);
        draw_rich_pine_tree(430, 30);
        draw_rich_pine_tree(450, 330);

        // Rich Log Cabin
        draw_rich_cabin(240, 40, g_player.has_lantern, g_fire_clock);

        // Player
        draw_rich_wanderer((int)g_player.x, (int)g_player.y, g_player.dir, g_player.walk_frame);

        // Weather particles
        for (const auto& s : g_snow) {
            draw_rect((int)s.x, (int)s.y, (int)s.size, (int)s.size, C_SNOW_WHITE);
        }
    } else {
        // ==========================================
        // CABIN INTERIOR ROOM
        // ==========================================
        // Wooden Floor Planks
        for (int y = 60; y < 400; y += 18) {
            draw_rect(80, y, 480, 16, C_WOOD_LOG);
            draw_rect(80, y + 16, 480, 2, C_WOOD_SHADOW);
        }
        // Walls
        draw_rect(80, 30, 480, 40, C_WOOD_SHADOW);

        // Fireplace with animated fire embers
        draw_rect(270, 35, 100, 50, 0x374151);
        draw_rect(285, 45, 70, 40, 0x180E08);
        g_fire_clock++;
        int flame_h = 15 + (g_fire_clock % 8);
        draw_rect(310, 80 - flame_h, 20, flame_h, C_FIRE_ORANGE);
        draw_rect(315, 80 - flame_h + 4, 10, flame_h - 4, C_YELLOW_TEXT);

        // Table with Cupboard
        draw_rect(120, 160, 70, 50, C_WOOD_SHADOW);
        draw_rect(125, 165, 60, 40, C_WOOD_LIGHT);
        if (!g_player.has_lantern) {
            // Draw glowing Brass Lantern on table
            draw_rect(148, 175, 14, 18, C_LANTERN_AMBER);
            draw_circle(155, 184, 4, 0xFEF08A);
        }

        // Exit Doorway to outside at bottom
        draw_rect(295, 385, 50, 15, 0x1E293B);
        draw_string("EXIT", 305, 370, C_SNOW_WHITE, 1);

        // Player inside
        draw_rich_wanderer((int)g_player.x, (int)g_player.y, g_player.dir, g_player.walk_frame);
    }

    // Top HUD Bar
    draw_rect(0, 0, INTERNAL_W, 26, 0x06090F);
    draw_string("IN THE PINES 2D (UNDERTALE RETRO)", 15, 7, C_WHITE, 2);
    draw_string("HP 20/20", 470, 7, C_YELLOW_TEXT, 2);
    draw_string(g_fullscreen ? "[F11] WINDOW" : "[F11] FULLSCREEN", 560, 8, C_ICE_BLUE, 1);

    // Interaction Prompt Icon above player head: "[!] PRESS Z"
    if (!g_interact_prompt.empty() && !g_dialog_open) {
        draw_rect((int)g_player.x - 20, (int)g_player.y - 20, 60, 15, C_BLACK);
        draw_rect_outline((int)g_player.x - 20, (int)g_player.y - 20, 60, 15, 2, C_YELLOW_TEXT);
        draw_string(g_interact_prompt, (int)g_player.x - 16, (int)g_player.y - 17, C_YELLOW_TEXT, 1);
    }

    // Undertale Dialog Box
    if (g_dialog_open) {
        draw_rect(30, 340, 580, 120, C_BLACK);
        draw_rect_outline(30, 340, 580, 120, 4, C_WHITE);
        draw_string(g_dialog_line1, 50, 360, C_WHITE, 2);
        draw_string(g_dialog_line2, 50, 390, C_WHITE, 2);
        draw_string("[PRESS Z OR ENTER TO CONTINUE]", 360, 435, C_YELLOW_TEXT, 1);
    }
}

// ==============================================================
// 5. BATTLE RENDERER
// ==============================================================
void render_battle() {
    clear_buffer(C_BLACK);

    int sx = (g_battle.shake > 0) ? (rand() % 7 - 3) : 0;
    int sy = (g_battle.shake > 0) ? (rand() % 7 - 3) : 0;
    if (g_battle.shake > 0) g_battle.shake--;

    uint32_t ghost_color = g_battle.enemy_pacified ? C_YELLOW_TEXT : C_WHITE;
    draw_circle(320 + sx, 90 + sy, 22, ghost_color);
    draw_rect(300 + sx, 112 + sy, 40, 50, ghost_color);
    draw_circle(313 + sx, 88 + sy, 3, 0x000000);
    draw_circle(327 + sx, 88 + sy, 3, 0x000000);

    draw_string(g_battle.enemy_pacified ? "* LOST GIRL (SPAREABLE)" : "* LOST GIRL", 220, 35, ghost_color, 2);

    draw_rect_outline(g_battle.box_x, g_battle.box_y, g_battle.box_w, g_battle.box_h, 4, C_WHITE);

    if (g_battle.turn == 1) {
        draw_soul_heart((int)g_battle.soul_x, (int)g_battle.soul_y, C_SOUL_RED);
        for (const auto& b : g_bullets) {
            draw_circle((int)b.x, (int)b.y, (int)b.r, C_ICE_BLUE);
        }
    } else if (g_battle.turn == 2) {
        draw_rect_outline(g_battle.box_x + 10, g_battle.box_y + 45, g_battle.box_w - 20, 45, 2, C_ICE_BLUE);
        draw_rect(g_battle.box_x + g_battle.box_w / 2 - 15, g_battle.box_y + 45, 30, 45, C_YELLOW_TEXT);
        draw_rect(g_battle.box_x + 10 + (int)g_battle.timing_x, g_battle.box_y + 40, 8, 55, C_WHITE);
        draw_string("PRESS [Z / ENTER] ON YELLOW TO STRUM!", g_battle.box_x + 15, g_battle.box_y + 105, C_WHITE, 1);
    } else {
        draw_string("* The cold wind weeps through her dress.", g_battle.box_x + 15, g_battle.box_y + 30, C_WHITE, 2);
        draw_string("* What will you play?", g_battle.box_x + 15, g_battle.box_y + 60, C_WHITE, 2);
    }

    draw_string("KURT   LV 1   HP 20 / 20", 170, 375, C_WHITE, 2);
    draw_rect(380, 372, 80, 16, C_SOUL_RED);
    draw_rect(380, 372, (int)(80.0f * (g_player.hp / 20.0f)), 16, C_YELLOW_TEXT);

    const char* btn_labels[4] = {"[ STRUM ]", "[ ACT ]", "[ ITEM ]", "[ MERCY ]"};
    int bx = 50;
    for (int i = 0; i < 4; i++) {
        bool sel = (g_battle.turn == 0 && g_battle.selected_btn == i);
        draw_rect_outline(bx, 415, 125, 40, 3, sel ? C_ORANGE_BTN : 0xC2410C);
        draw_string(btn_labels[i], bx + 16, 428, sel ? C_YELLOW_TEXT : 0xC2410C, 2);
        if (sel) draw_soul_heart(bx + 8, 435, C_SOUL_RED);
        bx += 140;
    }
}

// ==============================================================
// 6. WIN32 ENTRY POINT & 60 FPS SCALED BLIT
// ==============================================================
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    if (msg == WM_DESTROY) {
        PostQuitMessage(0);
        return 0;
    }
    if (msg == WM_KEYDOWN) {
        if (wParam == VK_F11) {
            toggle_fullscreen(hwnd);
            return 0;
        }
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE, LPSTR, int nCmdShow) {
    for (int i = 0; i < 60; i++) {
        g_snow.push_back({(float)(rand() % INTERNAL_W), (float)(rand() % INTERNAL_H), 1.2f + (rand() % 15) / 10.0f, (float)(1 + rand() % 3)});
    }

    WNDCLASS wc = {0};
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = "InThePinesUndertalePro";
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    RegisterClass(&wc);

    HWND hwnd = CreateWindow("InThePinesUndertalePro", "IN THE PINES - 2D Undertale Edition",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, INTERNAL_W + 16, INTERNAL_H + 39,
        NULL, NULL, hInstance, NULL);

    ShowWindow(hwnd, nCmdShow);

    BITMAPINFO bmi = {0};
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = INTERNAL_W;
    bmi.bmiHeader.biHeight = -INTERNAL_H;
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    HDC hdc = GetDC(hwnd);

    MSG msg;
    bool running = true;
    DWORD last_tick = GetTickCount();

    // Initial dialogue
    g_dialog_open = true;
    g_dialog_line1 = "* 03:17 AM. Dense mist swirls around the pines.";
    g_dialog_line2 = "* Slung on your back is your acoustic guitar.";

    while (running) {
        while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
            if (msg.message == WM_QUIT) running = false;
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }

        DWORD cur_tick = GetTickCount();
        if (cur_tick - last_tick < 16) {
            Sleep(1);
            continue;
        }
        last_tick = cur_tick;

        if (g_state == STATE_OVERWORLD) {
            bool moving = false;
            if (!g_dialog_open) {
                if (GetAsyncKeyState(VK_UP) & 0x8000 || GetAsyncKeyState('W') & 0x8000) { g_player.y -= 2.6f; g_player.dir = 2; moving = true; }
                if (GetAsyncKeyState(VK_DOWN) & 0x8000 || GetAsyncKeyState('S') & 0x8000) { g_player.y += 2.6f; g_player.dir = 0; moving = true; }
                if (GetAsyncKeyState(VK_LEFT) & 0x8000 || GetAsyncKeyState('A') & 0x8000) { g_player.x -= 2.6f; g_player.dir = 3; moving = true; }
                if (GetAsyncKeyState(VK_RIGHT) & 0x8000 || GetAsyncKeyState('D') & 0x8000) { g_player.x += 2.6f; g_player.dir = 1; moving = true; }
            }

            if (moving) {
                g_player.walk_timer++;
                if (g_player.walk_timer % 10 == 0) {
                    g_player.walk_frame++;
                    g_footprints.push_back({(int)g_player.x + 8, (int)g_player.y + 28, 1.0f});
                }
            }

            // Interactable Proximity Checks
            g_interact_prompt = "";
            if (g_loc == LOC_OUTSIDE) {
                // Near Cabin Door?
                if (g_player.x > 290 && g_player.x < 330 && g_player.y > 115 && g_player.y < 155) {
                    g_interact_prompt = "[Z] ENTER";
                }
                // Near Railroad wheel?
                else if (g_player.x > 500 && g_player.y > 170 && g_player.y < 250) {
                    g_interact_prompt = "[Z] EXAMINE";
                }
            } else {
                // Inside Cabin: Near Cupboard Table?
                if (g_player.x > 110 && g_player.x < 200 && g_player.y > 140 && g_player.y < 210) {
                    g_interact_prompt = g_player.has_lantern ? "[Z] TABLE" : "[Z] TAKE LANTERN";
                }
                // Near Fireplace?
                else if (g_player.x > 280 && g_player.x < 360 && g_player.y < 120) {
                    g_interact_prompt = "[Z] WARM UP";
                }
                // Near Exit Door?
                else if (g_player.y > 360) {
                    g_interact_prompt = "[Z] EXIT CABIN";
                }
            }

            // [Z] or [Enter] to Interact
            static bool z_key = false;
            if (GetAsyncKeyState('Z') & 0x8000 || GetAsyncKeyState(VK_RETURN) & 0x8000) {
                if (!z_key) {
                    z_key = true;
                    if (g_dialog_open) {
                        g_dialog_open = false; // Close dialogue
                    } else if (!g_interact_prompt.empty()) {
                        if (g_loc == LOC_OUTSIDE) {
                            if (g_interact_prompt == "[Z] ENTER") {
                                g_loc = LOC_INSIDE_CABIN;
                                g_player.x = 310; g_player.y = 350;
                                Beep(440, 100);
                            } else if (g_interact_prompt == "[Z] EXAMINE") {
                                g_dialog_open = true;
                                g_dialog_line1 = "* Initial 'K' is gouged into the wheel hub.";
                                g_dialog_line2 = "* Blonde hair is locked into the iron bolts!";
                                g_player.has_hairpin = true;
                                Beep(220, 150);
                            }
                        } else {
                            if (g_interact_prompt == "[Z] TAKE LANTERN") {
                                g_player.has_lantern = true;
                                g_dialog_open = true;
                                g_dialog_line1 = "* You picked up the Brass Kerosene Lantern!";
                                g_dialog_line2 = "* (Its warm amber glow pushes back the dark.)";
                                Beep(554, 150);
                            } else if (g_interact_prompt == "[Z] WARM UP") {
                                g_dialog_open = true;
                                g_dialog_line1 = "* The hearth fire crackles softly.";
                                g_dialog_line2 = "* (Your frozen fingers are starting to thaw.)";
                                Beep(330, 120);
                            } else if (g_interact_prompt == "[Z] EXIT CABIN") {
                                g_loc = LOC_OUTSIDE;
                                g_player.x = 310; g_player.y = 165;
                                Beep(300, 100);
                            }
                        }
                    }
                }
            } else { z_key = false; }

            // 'B' triggers boss battle
            static bool b_key = false;
            if (GetAsyncKeyState('B') & 0x8000) {
                if (!b_key) {
                    b_key = true;
                    g_state = STATE_BATTLE;
                    g_battle.turn = 0;
                    MessageBeep(MB_OK);
                }
            } else { b_key = false; }

            // Snow & Footprint update
            for (auto& s : g_snow) {
                s.y += s.speed; s.x -= 0.4f;
                if (s.y > INTERNAL_H) { s.y = 0; s.x = rand() % INTERNAL_W; }
            }
            for (auto& fp : g_footprints) fp.life -= 0.005f;
            while (!g_footprints.empty() && g_footprints.front().life <= 0) g_footprints.erase(g_footprints.begin());

            render_overworld();
        }

        else if (g_state == STATE_BATTLE) {
            // Battle Controls
            if (g_battle.turn == 0) {
                static bool arr_key = false;
                if (GetAsyncKeyState(VK_LEFT) & 0x8000) {
                    if (!arr_key) { g_battle.selected_btn = (g_battle.selected_btn + 3) % 4; arr_key = true; MessageBeep(0xFFFFFFFF); }
                } else if (GetAsyncKeyState(VK_RIGHT) & 0x8000) {
                    if (!arr_key) { g_battle.selected_btn = (g_battle.selected_btn + 1) % 4; arr_key = true; MessageBeep(0xFFFFFFFF); }
                } else if (GetAsyncKeyState('Z') & 0x8000 || GetAsyncKeyState(VK_RETURN) & 0x8000) {
                    if (!arr_key) {
                        arr_key = true;
                        if (g_battle.selected_btn == 0) { g_battle.turn = 2; g_battle.timing_x = 0; }
                        else if (g_battle.selected_btn == 3) { g_state = STATE_OVERWORLD; }
                        else { g_battle.turn = 1; g_battle.turn_timer = 0; g_bullets.clear(); }
                    }
                } else { arr_key = false; }
            } else if (g_battle.turn == 1) {
                g_battle.turn_timer++;
                if (GetAsyncKeyState(VK_UP) & 0x8000) g_battle.soul_y -= 3.2f;
                if (GetAsyncKeyState(VK_DOWN) & 0x8000) g_battle.soul_y += 3.2f;
                if (GetAsyncKeyState(VK_LEFT) & 0x8000) g_battle.soul_x -= 3.2f;
                if (GetAsyncKeyState(VK_RIGHT) & 0x8000) g_battle.soul_x += 3.2f;

                g_battle.soul_x = max(g_battle.box_x + 10.0f, min(g_battle.box_x + g_battle.box_w - 10.0f, g_battle.soul_x));
                g_battle.soul_y = max(g_battle.box_y + 10.0f, min(g_battle.box_y + g_battle.box_h - 10.0f, g_battle.soul_y));

                if (g_battle.turn_timer % 16 == 0) {
                    g_bullets.push_back({(float)(g_battle.box_x + 15 + rand() % (g_battle.box_w - 30)), (float)(g_battle.box_y + 6), (float)((rand() % 20 - 10) / 10.0f), 2.4f + (rand() % 10) / 10.0f, 4.0f});
                }

                for (size_t i = 0; i < g_bullets.size(); ) {
                    g_bullets[i].x += g_bullets[i].vx;
                    g_bullets[i].y += g_bullets[i].vy;

                    float dist = hypot(g_bullets[i].x - g_battle.soul_x, g_bullets[i].y - g_battle.soul_y);
                    if (dist < g_bullets[i].r + 6.0f) {
                        g_player.hp = max(1, g_player.hp - 2);
                        g_battle.shake = 6;
                        MessageBeep(MB_ICONHAND);
                        g_bullets.erase(g_bullets.begin() + i);
                        continue;
                    }

                    if (g_bullets[i].y > g_battle.box_y + g_battle.box_h) {
                        g_bullets.erase(g_bullets.begin() + i);
                    } else {
                        i++;
                    }
                }

                if (g_battle.turn_timer > 240) {
                    g_battle.turn = 0;
                    g_bullets.clear();
                }
            } else if (g_battle.turn == 2) {
                g_battle.timing_x += 5.5f;
                static bool strum_hit = false;
                if (GetAsyncKeyState('Z') & 0x8000 || GetAsyncKeyState(VK_RETURN) & 0x8000) {
                    if (!strum_hit) {
                        strum_hit = true;
                        float center = (g_battle.box_w - 20) / 2.0f;
                        if (fabs(g_battle.timing_x - center) < 30.0f) {
                            g_battle.enemy_hp -= 35;
                            g_battle.enemy_pacified = true;
                            Beep(330, 200);
                        }
                        g_battle.turn = 1;
                        g_battle.turn_timer = 0;
                        g_bullets.clear();
                    }
                } else { strum_hit = false; }

                if (g_battle.timing_x > g_battle.box_w - 20) {
                    g_battle.turn = 1;
                    g_battle.turn_timer = 0;
                    g_bullets.clear();
                }
            }

            render_battle();
        }

        // Scaled Aspect-Ratio Blit (Maintains crisp pixel art in Window or Fullscreen!)
        RECT client_rect;
        GetClientRect(hwnd, &client_rect);
        int win_w = client_rect.right - client_rect.left;
        int win_h = client_rect.bottom - client_rect.top;

        StretchDIBits(hdc, 0, 0, win_w, win_h, 0, 0, INTERNAL_W, INTERNAL_H, framebuffer, &bmi, DIB_RGB_COLORS, SRCCOPY);
    }

    ReleaseDC(hwnd, hdc);
    return 0;
}
