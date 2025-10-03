#include <stdlib.h>
#include <windows.h>
#include <stdio.h>
#include "data_tools.h"

struct Doc_Charcter{
    int font;
    int color_r;
    int color_g;
    int color_b;
    bool bold;
    bool itelic;
    int CharacterCode;
}typedef DC_;
struct Line {
    DC_* character;
    int pos;
    struct Line* nextCharacter;
}typedef LI_;
struct Book {
    LI_ *l;
    int pos;
    struct Book* nextLine;
}typedef Book;
struct CursorPos {
    int x;
    int y;
}typedef Cursor;

static Book* BKData;
static Cursor* cursor;

int makeBook();
int makeCursor();
int isCursor();
int atCursor(int x, int y);
int setCursorPos(int x, int y);
int addCharacter(DC_* CharData);

int BK_All_Line();
int BK_ALL_CharPos();
int BK_Current_Line();
int BK_Current_CharPos();