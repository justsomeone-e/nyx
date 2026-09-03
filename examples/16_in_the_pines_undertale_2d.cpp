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
// 1. CONSTANTS & 32-BIT COLOR PALETTE
// ==============================================================
const int SCREEN_W = 640;
const int SCREEN_H = 480;
uint32_t framebuffer[SCREEN_W * SCREEN_H];

// Color definitions (0x00RRGGBB)
const uint32_t C_BLACK       = 0x000000;
const uint32_t C_WHITE       = 0xFFFFFF;
const uint32_t C_SNOW_NIGHT  = 0x0A0E17;
const uint32_t C_PINE_DARK   = 0x0D1F15;
const uint32_t C_PINE_MED    = 0x183827;
const uint32_t C_PINE_LIGHT  = 0x224D36;
const uint32_t C_SNOW_WHITE  = 0xE2E8F0;
const uint32_t C_SNOW_SHADOW = 0x94A3B8;
const uint32_t C_WOOD_DARK   = 0x2B1810;
const uint32_t C_WOOD_MED    = 0x4A2C1D;
const uint32_t C_WOOD_LIGHT  = 0x6E442F;
const uint32_t C_SOUL_RED    = 0xFF0000;
const uint32_t C_LANTERN_GLOW= 0xF59E0B;
const uint32_t C_ICE_BLUE    = 0x38BDF8;
const uint32_t C_YELLOW_TEXT = 0xFFFF00;
const uint32_t C_ORANGE_BTN  = 0xFF9900;
const uint32_t C_RAIL_STEEL  = 0x475569;
const uint32_t C_GRAVESTONE  = 0x64748B;

// ==============================================================
// 2. PROCEDURAL PIXEL DRAWING PRIMITIVES
// ==============================================================
inline void put_pixel(int x, int y, uint32_t color) {
    if (x >= 0 && x < SCREEN_W && y >= 0 && y < SCREEN_H) {
        framebuffer[y * SCREEN_W + x] = color;
    }
}

void clear_buffer(uint32_t color) {
    for (int i = 0; i < SCREEN_W * SCREEN_H; i++) framebuffer[i] = color;
}

void draw_rect(int rx, int ry, int rw, int rh, uint32_t color) {
    int x1 = max(0, rx);
    int y1 = max(0, ry);
    int x2 = min(SCREEN_W, rx + rw);
    int y2 = min(SCREEN_H, ry + rh);
    for (int y = y1; y < y2; y++) {
        for (int x = x1; x < x2; x++) {
            framebuffer[y * SCREEN_W + x] = color;
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

// Procedural Undertale Red Soul Heart
void draw_soul_heart(int hx, int hy, uint32_t color) {
    // 12x12 Pixel Art Heart
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

// Procedural Multi-layered Snow Pine Tree
void draw_pixel_pine_tree(int tx, int ty) {
    // Tree Trunk with bark shadows
    draw_rect(tx + 18, ty + 50, 10, 24, C_WOOD_DARK);
    draw_rect(tx + 20, ty + 50, 4, 24, C_WOOD_MED);

    // Layer 3 (Bottom bough)
    for (int y = 0; y < 22; y++) {
        int w = y * 2 + 6;
        draw_rect(tx + 23 - w / 2, ty + 36 + y, w, 1, C_PINE_DARK);
    }
    // Snow on Layer 3
    draw_rect(tx + 4, ty + 46, 38, 4, C_SNOW_WHITE);
    draw_rect(tx + 7, ty + 44, 32, 2, C_SNOW_SHADOW);

    // Layer 2 (Middle bough)
    for (int y = 0; y < 20; y++) {
        int w = y * 2 + 4;
        draw_rect(tx + 23 - w / 2, ty + 18 + y, w, 1, C_PINE_MED);
    }
    // Snow on Layer 2
    draw_rect(tx + 8, ty + 28, 30, 3, C_SNOW_WHITE);

    // Layer 1 (Top crown)
    for (int y = 0; y < 18; y++) {
        int w = y * 2 + 2;
        draw_rect(tx + 23 - w / 2, ty + y, w, 1, C_PINE_LIGHT);
    }
    // Snow on Crown tip
    draw_rect(tx + 18, ty + 4, 10, 3, C_SNOW_WHITE);
}

// Procedural Wanderer / Kurt Sprite (20x30 pixels)
void draw_pixel_wanderer(int px, int py, int dir, int walk_frame) {
    int leg_offset = (walk_frame % 2 == 0) ? 0 : 2;

    // 1. Acoustic Martin Guitar strapped to back (Wooden Body, Soundhole, Neck)
    int gx = (dir == 1) ? (px + 14) : (px - 6); // Shift based on facing
    draw_rect(gx, py + 8, 8, 16, 0xD97706);      // Warm honey mahogany wood
    draw_circle(gx + 4, py + 16, 2, 0x1E140A);   // Soundhole
    draw_rect(gx + 2, py, 4, 9, 0xFEF08A);       // Maple neck and headstock

    // 2. Parka Coat Body (Dark Teal & Fold shadows)
    draw_rect(px, py + 10, 16, 15, 0x0369A1);
    draw_rect(px + 3, py + 12, 10, 13, 0x0284C7);

    // 3. Warm Winter Scarf
    draw_rect(px - 1, py + 8, 18, 4, 0xBE123C); // Crimson scarf

    // 4. Face & Messy Grunge Hair
    draw_rect(px + 3, py + 2, 10, 7, 0xFED7AA); // Pale skin
    draw_rect(px + 1, py - 2, 14, 5, 0xCA8A04); // Blonde grunge hair falling
    draw_rect(px + 2, py + 1, 3, 4, 0xA16207);  // Hair strands

    // 5. Boots in Snow (Walking animation)
    draw_rect(px + 2, py + 25, 4, 6 - leg_offset, 0x1E293B);
    draw_rect(px + 10, py + 25, 4, 6 + leg_offset, 0x1E293B);
}

// ==============================================================
// 3. GAME STATE & WORLD ENTITIES
// ==============================================================
enum GameState { STATE_OVERWORLD, STATE_BATTLE, STATE_ENDING };
GameState g_state = STATE_OVERWORLD;

struct Player {
    float x = 320;
    float y = 360;
    int dir = 0; // 0: Down, 1: Right, 2: Up, 3: Left
    int walk_frame = 0;
    int walk_timer = 0;
    int hp = 20;
    int max_hp = 20;
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

// Undertale Battle Soul & Box
struct BattleSystem {
    float soul_x = 320;
    float soul_y = 280;
    int box_x = 190;
    int box_y = 190;
    int box_w = 260;
    int box_h = 140;
    int selected_btn = 0; // 0: STRUM, 1: ACT, 2: ITEM, 3: MERCY
    int turn = 0;         // 0: Player Menu, 1: Enemy Attack, 2: Strum Timing Bar
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

// Simple Monospace 5x7 Font Renderer for In-Game Text
void draw_char(char c, int x, int y, uint32_t color, int scale = 2) {
    // 5x7 bitmap representation of common ASCII characters
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
            cur_y += 9 * scale;
            continue;
        }
        draw_char(c, cur_x, cur_y, color, scale);
        cur_x += 6 * scale;
    }
}

// ==============================================================
// 4. OVERWORLD & BATTLE RENDER LOOPS
// ==============================================================
void update_overworld() {
    // Footprint decay
    for (size_t i = 0; i < g_footprints.size(); i++) {
        g_footprints[i].life -= 0.005f;
    }
    while (!g_footprints.empty() && g_footprints.front().life <= 0) {
        g_footprints.erase(g_footprints.begin());
    }

    // Snow update
    for (auto& s : g_snow) {
        s.y += s.speed;
        s.x -= 0.4f;
        if (s.y > SCREEN_H) { s.y = 0; s.x = rand() % SCREEN_W; }
    }
}

void render_overworld() {
    clear_buffer(C_SNOW_NIGHT);

    // Footprints
    for (const auto& fp : g_footprints) {
        draw_rect(fp.x, fp.y, 4, 3, 0x141F30);
    }

    // Railroad on the right
    draw_rect(530, 0, 8, SCREEN_H, C_RAIL_STEEL);
    draw_rect(570, 0, 8, SCREEN_H, C_RAIL_STEEL);
    for (int y = 0; y < SCREEN_H; y += 22) {
        draw_rect(520, y, 68, 5, C_WOOD_DARK);
    }

    // Locomotive Drive Wheel
    draw_circle(554, 210, 26, 0x64748B);
    draw_circle(554, 210, 15, 0x1E293B);
    draw_rect(550, 190, 8, 40, 0x94A3B8);

    // Pine Trees
    draw_pixel_pine_tree(40, 40);
    draw_pixel_pine_tree(130, 20);
    draw_pixel_pine_tree(50, 280);
    draw_pixel_pine_tree(120, 360);
    draw_pixel_pine_tree(440, 40);
    draw_pixel_pine_tree(460, 340);

    // Abandoned Cabin
    draw_rect(250, 50, 140, 100, C_WOOD_DARK);
    draw_rect(240, 36, 160, 18, C_WOOD_MED);    // Roof
    draw_rect(245, 34, 150, 4, C_SNOW_WHITE);   // Snow on roof
    draw_rect(305, 105, 30, 45, 0x180F0A);      // Door
    draw_rect(265, 80, 24, 24, g_player.has_lantern ? C_LANTERN_GLOW : 0x1E293B); // Window

    // Player
    draw_pixel_wanderer((int)g_player.x, (int)g_player.y, g_player.dir, g_player.walk_frame);

    // Snow Flurries
    for (const auto& s : g_snow) {
        draw_rect((int)s.x, (int)s.y, (int)s.size, (int)s.size, C_SNOW_WHITE);
    }

    // Top HUD Bar
    draw_rect(0, 0, SCREEN_W, 28, 0x05080E);
    draw_string("IN THE PINES 2D (UNDERTALE EDITION)", 20, 7, C_WHITE, 2);
    draw_string("HP 20/20", 470, 7, C_YELLOW_TEXT, 2);
    draw_string("CLUES 0/4", 570, 7, C_ICE_BLUE, 2);

    // Bottom Undertale Dialog Box
    draw_rect(30, 340, 580, 120, C_BLACK);
    draw_rect_outline(30, 340, 580, 120, 4, C_WHITE);
    draw_string("* 03:17 AM. Dense mist swirls around the pines.", 50, 360, C_WHITE, 2);
    draw_string("* (Slung on your back is a nylon-string guitar.)", 50, 385, C_WHITE, 2);
    draw_string("* [ARROW KEYS] Walk  |  [B] Trigger VS Boss Fight!", 50, 415, C_YELLOW_TEXT, 2);
}

void render_battle() {
    clear_buffer(C_BLACK);

    // Shake
    int sx = (g_battle.shake > 0) ? (rand() % 7 - 3) : 0;
    int sy = (g_battle.shake > 0) ? (rand() % 7 - 3) : 0;
    if (g_battle.shake > 0) g_battle.shake--;

    // Boss: The Ghost of the Pines (Spectral dress & glowing eyes)
    uint32_t ghost_color = g_battle.enemy_pacified ? C_YELLOW_TEXT : C_WHITE;
    draw_circle(320 + sx, 90 + sy, 22, ghost_color);
    draw_rect(300 + sx, 112 + sy, 40, 50, ghost_color);
    draw_circle(313 + sx, 88 + sy, 3, 0x000000); // Eyes
    draw_circle(327 + sx, 88 + sy, 3, 0x000000);

    draw_string(g_battle.enemy_pacified ? "* LOST GIRL (SPAREABLE)" : "* LOST GIRL", 220, 35, ghost_color, 2);

    // Undertale Battle Arena Box
    draw_rect_outline(g_battle.box_x, g_battle.box_y, g_battle.box_w, g_battle.box_h, 4, C_WHITE);

    if (g_battle.turn == 1) {
        // ENEMY TURN: Draw Red Soul & Bullets
        draw_soul_heart((int)g_battle.soul_x, (int)g_battle.soul_y, C_SOUL_RED);

        for (const auto& b : g_bullets) {
            draw_circle((int)b.x, (int)b.y, (int)b.r, C_ICE_BLUE);
        }
    } else if (g_battle.turn == 2) {
        // TIMING BAR: Strum Game
        draw_rect_outline(g_battle.box_x + 10, g_battle.box_y + 45, g_battle.box_w - 20, 45, 2, C_ICE_BLUE);
        draw_rect(g_battle.box_x + g_battle.box_w / 2 - 15, g_battle.box_y + 45, 30, 45, C_YELLOW_TEXT);
        draw_rect(g_battle.box_x + 10 + (int)g_battle.timing_x, g_battle.box_y + 40, 8, 55, C_WHITE);
        draw_string("PRESS [Z / ENTER] ON YELLOW TO STRUM!", g_battle.box_x + 15, g_battle.box_y + 105, C_WHITE, 1);
    } else {
        // Player Menu Text
        draw_string("* The air smells like wet cedar needles.", g_battle.box_x + 15, g_battle.box_y + 30, C_WHITE, 2);
        draw_string("* What will you play?", g_battle.box_x + 15, g_battle.box_y + 60, C_WHITE, 2);
    }

    // Player HP
    draw_string("KURT   LV 1   HP 20 / 20", 170, 375, C_WHITE, 2);
    draw_rect(380, 372, 80, 16, C_SOUL_RED);
    draw_rect(380, 372, (int)(80.0f * (g_player.hp / 20.0f)), 16, C_YELLOW_TEXT);

    // 4 Undertale Buttons
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
// 5. WIN32 MAIN & MESSAGE LOOP
// ==============================================================
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    if (msg == WM_DESTROY) {
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE, LPSTR, int nCmdShow) {
    // Seed snow
    for (int i = 0; i < 60; i++) {
        g_snow.push_back({(float)(rand() % SCREEN_W), (float)(rand() % SCREEN_H), 1.2f + (rand() % 15) / 10.0f, (float)(1 + rand() % 3)});
    }

    WNDCLASS wc = {0};
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = "InThePinesUndertale";
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    RegisterClass(&wc);

    HWND hwnd = CreateWindow("InThePinesUndertale", "IN THE PINES — 2D Undertale Edition",
        WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, SCREEN_W + 16, SCREEN_H + 39,
        NULL, NULL, hInstance, NULL);

    ShowWindow(hwnd, nCmdShow);

    BITMAPINFO bmi = {0};
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = SCREEN_W;
    bmi.bmiHeader.biHeight = -SCREEN_H; // Top-down DIB
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    HDC hdc = GetDC(hwnd);

    MSG msg;
    bool running = true;
    DWORD last_tick = GetTickCount();

    while (running) {
        while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
            if (msg.message == WM_QUIT) running = false;
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }

        // 60 FPS tick clamp
        DWORD cur_tick = GetTickCount();
        if (cur_tick - last_tick < 16) {
            Sleep(1);
            continue;
        }
        last_tick = cur_tick;

        // Input Handling
        if (g_state == STATE_OVERWORLD) {
            bool moving = false;
            if (GetAsyncKeyState(VK_UP) & 0x8000 || GetAsyncKeyState('W') & 0x8000) { g_player.y -= 2.6f; g_player.dir = 2; moving = true; }
            if (GetAsyncKeyState(VK_DOWN) & 0x8000 || GetAsyncKeyState('S') & 0x8000) { g_player.y += 2.6f; g_player.dir = 0; moving = true; }
            if (GetAsyncKeyState(VK_LEFT) & 0x8000 || GetAsyncKeyState('A') & 0x8000) { g_player.x -= 2.6f; g_player.dir = 3; moving = true; }
            if (GetAsyncKeyState(VK_RIGHT) & 0x8000 || GetAsyncKeyState('D') & 0x8000) { g_player.x += 2.6f; g_player.dir = 1; moving = true; }

            if (moving) {
                g_player.walk_timer++;
                if (g_player.walk_timer % 10 == 0) {
                    g_player.walk_frame++;
                    g_footprints.push_back({(int)g_player.x + 6, (int)g_player.y + 26, 1.0f});
                }
            }

            // 'B' triggers boss fight
            static bool b_pressed = false;
            if (GetAsyncKeyState('B') & 0x8000) {
                if (!b_pressed) {
                    b_pressed = true;
                    g_state = STATE_BATTLE;
                    g_battle.turn = 0;
                    MessageBeep(MB_OK);
                }
            } else { b_pressed = false; }

            update_overworld();
            render_overworld();
        }

        else if (g_state == STATE_BATTLE) {
            // Battle Controls
            if (g_battle.turn == 0) {
                static bool arrow_pressed = false;
                if (GetAsyncKeyState(VK_LEFT) & 0x8000) {
                    if (!arrow_pressed) { g_battle.selected_btn = (g_battle.selected_btn + 3) % 4; arrow_pressed = true; MessageBeep(0xFFFFFFFF); }
                } else if (GetAsyncKeyState(VK_RIGHT) & 0x8000) {
                    if (!arrow_pressed) { g_battle.selected_btn = (g_battle.selected_btn + 1) % 4; arrow_pressed = true; MessageBeep(0xFFFFFFFF); }
                } else if (GetAsyncKeyState('Z') & 0x8000 || GetAsyncKeyState(VK_RETURN) & 0x8000) {
                    if (!arrow_pressed) {
                        arrow_pressed = true;
                        if (g_battle.selected_btn == 0) {
                            // STRUM
                            g_battle.turn = 2;
                            g_battle.timing_x = 0;
                        } else if (g_battle.selected_btn == 3) {
                            // MERCY -> Return to overworld
                            g_state = STATE_OVERWORLD;
                        } else {
                            // ACT / ITEM -> Enemy Turn
                            g_battle.turn = 1;
                            g_battle.turn_timer = 0;
                            g_bullets.clear();
                        }
                    }
                } else { arrow_pressed = false; }
            } else if (g_battle.turn == 1) {
                // Enemy Bullet Hell
                g_battle.turn_timer++;
                if (GetAsyncKeyState(VK_UP) & 0x8000) g_battle.soul_y -= 3.2f;
                if (GetAsyncKeyState(VK_DOWN) & 0x8000) g_battle.soul_y += 3.2f;
                if (GetAsyncKeyState(VK_LEFT) & 0x8000) g_battle.soul_x -= 3.2f;
                if (GetAsyncKeyState(VK_RIGHT) & 0x8000) g_battle.soul_x += 3.2f;

                // Box bounds
                g_battle.soul_x = max(g_battle.box_x + 10.0f, min(g_battle.box_x + g_battle.box_w - 10.0f, g_battle.soul_x));
                g_battle.soul_y = max(g_battle.box_y + 10.0f, min(g_battle.box_y + g_battle.box_h - 10.0f, g_battle.soul_y));

                // Spawn bullets
                if (g_battle.turn_timer % 16 == 0) {
                    g_bullets.push_back({(float)(g_battle.box_x + 15 + rand() % (g_battle.box_w - 30)), (float)(g_battle.box_y + 6), (float)((rand() % 20 - 10) / 10.0f), 2.4f + (rand() % 10) / 10.0f, 4.0f});
                }

                // Bullets update & hit
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
                // Timing Bar
                g_battle.timing_x += 5.5f;
                static bool z_hit = false;
                if (GetAsyncKeyState('Z') & 0x8000 || GetAsyncKeyState(VK_RETURN) & 0x8000) {
                    if (!z_hit) {
                        z_hit = true;
                        float center = (g_battle.box_w - 20) / 2.0f;
                        if (fabs(g_battle.timing_x - center) < 30.0f) {
                            // Perfect Strum!
                            g_battle.enemy_hp -= 35;
                            g_battle.enemy_pacified = true;
                            Beep(330, 200); // E chord frequency
                        }
                        g_battle.turn = 1;
                        g_battle.turn_timer = 0;
                        g_bullets.clear();
                    }
                } else { z_hit = false; }

                if (g_battle.timing_x > g_battle.box_w - 20) {
                    g_battle.turn = 1;
                    g_battle.turn_timer = 0;
                    g_bullets.clear();
                }
            }

            render_battle();
        }

        // Blit 60 FPS buffer to Win32 screen
        StretchDIBits(hdc, 0, 0, SCREEN_W, SCREEN_H, 0, 0, SCREEN_W, SCREEN_H, framebuffer, &bmi, DIB_RGB_COLORS, SRCCOPY);
    }

    ReleaseDC(hwnd, hdc);
    return 0;
}
