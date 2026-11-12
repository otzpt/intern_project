#include "raylib.h"

#define RAYGUI_IMPLEMENTATION
#include <raygui.h>

#define FPS GetMonitorRefreshRate(GetCurrentMonitor())

void setup(void)
{
    InitWindow(600, 480, "teste");
    SetTargetFPS(FPS);
}

int main(void)
{
    setup();

    Rectangle btnMenu = {300, 200, 200, 50};

    while (!WindowShouldClose()) {
        BeginDrawing();
        ClearBackground(RAYWHITE);

        DrawText("ola ray", 20, 20, 24, DARKGRAY);

        if (GuiButton(btnMenu, "Ligar")) {
            // clicou
            GuiLabel((Rectangle){20, 20, 200, 24}, "Servidor: parado");
        }

        EndDrawing();
    }

    CloseWindow();
    return 0;
}
