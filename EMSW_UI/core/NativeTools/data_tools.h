#ifndef STACK_H
#define STACK_H

#include <stdlib.h>
#include <malloc.h>
#include <wchar.h>
#include <stdbool.h>
#include <stdio.h>

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

#define STACK_H
#define stack Stack
#define list List
#define dqueue D_Queue

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

#endif