#include "keyboardEvent.h"

// return 0 is format DC_
// return 1 is data hear, not format DC_.
int AppendWord(DC_* dc_t) {
    if (dc_t == NULL) {
        dc_t = (DC_*)malloc(sizeof(DC_));
        return 0;
    } else {
        return 1;
    }
}
// return 0 is format LI_
// return -1 is data hear, not format Line
int AppendLine(LI_ *line) {
    if (line == NULL) {
        line = (LI_*)malloc(sizeof(LI_));
        return (AppendWord(line->character))?0: 1;
    } else {
        return -1;
    }
}
// return 0 is create book
// return -1 is not create book, and memory in book.
// return -2 is cannot Create Book.
int makeBook() {
    if (BKData == NULL) {
        BKData = (Book*)malloc(sizeof(Book));
        int result = AppendLine(BKData->l)? 0: 1;
        if (result == 0) {
            BKData->l->pos = 0;
        } else {
            return -2;
        }
        BKData->pos = 0;
        return 0;
    } else {
        return -1;
    }
}
// return 0, can create Cursor
// return -1, is alived Cursor
int makeCursor() {
    if (cursor == NULL){
        cursor = (Cursor*)malloc(sizeof(Cursor));
        return 0;
    }
    else {
        return -1;
    }
}
// Cusor memory Check
// return 0, is make Cursor Succesful
// return 1, is Cursor alived
// return -1, is Cursor not alived, can not create cursor
int isCursor() {
    if (cursor != NULL) {
        return 0;
    } else if (cursor == NULL) {
        cursor = (Cursor*)malloc(sizeof(Cursor));
        cursor->x = 0;
        cursor->y = 0;
        return 1;
    }
    return -1;
}
// set Cursor position
// return 0 is success Cursor Pos
// return -1 cursor is NULL pointer
// return -2 cursor is can not Reach Line
// return -3 cursor is can not Reach Char
int setCursorPos(int x, int y) {
    if (cursor == NULL) {
        return -1;
    }
    cursor->x = x;
    cursor->y = 0;
    return 0;
}
// Cursor memory check, and set Cursor Pos
// return 0, set Cursor pos check.
// return -1, cannot set Cursor pos now
int atCursor(int x, int y) {
    int create = isCursor();
    if(create == 0?1:create == 1?1:0) {
        cursor->x = x;
        cursor->y = y;
        return 0;
    }
    return -1;
}
// FindLine
// if Line is alived, return memory ptr
// if Line is not alived, return NULL
LI_* getLine(Book* tmp) {
    if (tmp->pos == cursor->y) {
        return tmp->l;
    } else if (tmp->pos != cursor->y - 1 && tmp->nextLine == NULL) {
        return NULL;
    } else if (tmp->pos == cursor->y -1 && tmp->nextLine == NULL) {
        tmp->nextLine = (Book*)malloc(sizeof(Book));
        return tmp->nextLine;
    } else if (tmp->pos == 0) {
        tmp->pos = 1;
        return tmp->l;
    }
    return NULL;
}
// Find x Pos, and append CharData
// return 1 append Success
// return -1 do not append Success
int appendChar(DC_* CharData, LI_* tmp) {
    if (tmp->pos == cursor->x - 1 && tmp->nextCharacter != NULL) {
        LI_* m = tmp->nextCharacter;
        tmp->nextCharacter = (LI_*)malloc(sizeof(LI_))
        tmp->nextCharacter->character = CharData;
        tmp->nextCharacter->nextCharacter = m;
        return 1;
    } else if (tmp->pos == cursor->x - 1 && tmp->nextCharacter == NULL) {
        tmp->nextCharacter = (LI_*)malloc(sizeof(LI_))
        tmp->nextCharacter->character = CharData;
        tmp->nextCharacter->nextCharacter = NULL;
        return 1;
    }
    return -1;
}
int addCharacter(DC_* CharData) {
    if (cursor.x == 0 && cursor.y == 0) {
        BKData->l->character = CharData;
        cursor->y = 1;
        cursor->x = 1;
    }
    LI_* d = getLine(BKData);
    return appendChar(CharData, d);
}

int BK_All_Line() {
    return 0;
}
int BK_All_CharPos() {
    return 0;
}
int BK_Current_Line() {
    return 0;
}
int BK_Current_CharPos() {
    return 0;
}