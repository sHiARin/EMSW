#ifndef STACK_H
#define STACK_H

#include <stdlib.h>
#include <malloc.h>
#include <wchar.h>
#include <stdbool.h>
#include <stdio.h>
#include <windows.h>
#include <string.h>

struct stack {
    wchar_t* txt;
    struct stack* node;
} typedef Stack;
struct Node {
    Stack* data;
    struct Node* left;
    struct Node* right;
    int pos;
} typedef List;
struct DataQueueNode {
    struct DataQueueNode* back;
    Stack* data;
} typedef D_Queue;
// System event Queue
struct SystemEventNode {
    int event;
    struct SystemEventNode* node;
    ULONGLONG current_ms;
} typedef SE_Queue;
// windows Title, PID Memory
struct WindowData {
    int pid;
    wchar_t* title;
}typedef WIN_DATA;

// System Data Type define
#define STACK_H
#define stack Stack
#define list List
#define dqueue D_Queue
#define sequeue SE_Queue

// System Event value define
#define START_SYS 0xf220        // start system
#define DURING_SYS 0xf221       // running System
#define PRESSED_SYS 0xf222      // pressed system
#define FINISH_SYS 0xf223       // system is finished
#define KEY_SYS 0xf330          // keyboard signal
#define TIME_SYS 0xf331         // time value MSG

// System Status Message
#define ERROR_SYSTEM_QUEUE 0xffff   // system queue is error
#define NULL_QUE_ERR 0xfffe         // Null Queue error
#define SUCESS 0xfffd               // Sucess function
#define CONTINUE 0xfffc             // Continue function

__declspec(dllexport) stack* makeStack();                                                       // make stack for memory
__declspec(dllexport) stack* push(stack* st, wchar_t* txt);                                     // stack data push
__declspec(dllexport) wchar_t* pop(stack** st);                                                 // stack data pop
__declspec(dllexport) stack* copy(stack* st);                                                   // stack data copy
__declspec(dllexport) stack* getPtr(stack* st);                                                 // memory address return (using debug)
__declspec(dllexport) void freeStack(stack* st);                                                // freePtr
__declspec(dllexport) list* makeList();                                                         // make list node for memory
__declspec(dllexport) list* appendNode(list* n, stack* data);                                   // list append backward
__declspec(dllexport) list* appendForward(list* n, stack* data);                                // list append forward
__declspec(dllexport) int findPositionFromData(list* left, list* right, stack* data);           // search list position from data
__declspec(dllexport) stack* findDataFromPosition(list* left, list* right, int pos);            // search data from list position
__declspec(dllexport) void freeList(list* n);                                                   // remove List, and connect left node and right node
__declspec(dllexport) int len(list* n);                                                         // get List Length
__declspec(dllexport) int pos(list* n);                                                         // get node Pos
__declspec(dllexport) list* getLeft(list* n);                                                   // get Left Node
__declspec(dllexport) list* getRight(list* n);                                                  // get Right Node
__declspec(dllexport) bool isStart(list* n);                                                    // pos value is one
__declspec(dllexport) stack* getData(list* n);                                                  // get data from list
__declspec(dllexport) bool leftNone(list* n);                                                   // left node is None
__declspec(dllexport) bool rightNone(list* n);                                                  // right node is None
__declspec(dllexport) bool posCheck(list* n, int pos);                                          // node pos check
__declspec(dllexport) int appendLeft(list* left, stack* data, int pos);                         // append data left search
__declspec(dllexport) int appendRight(list* right, stack* data, int pos);                       // append data right search
__declspec(dllexport) int StartSystemQueue();                                                   // Create Sytem Queue
__declspec(dllexport) int SetStartMSG();                                                       // Set Start Message
__declspec(dllexport) int appendSystemMSG(int SysMSG);                                          // append System MSG
__declspec(dllexport) int appendSystemTime(ULONGLONG time);                                     // append SystemQueue to time MSG
__declspec(dllexport) int getSystemMSG();                                                       // append System MSG
__declspec(dllexport) int NullSystemQueue();                                                    // system queue is Null?

#endif