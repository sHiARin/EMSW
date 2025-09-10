#define UNICODE
#define _UNICODE

#include"data_tools.h"

// shift_pos_right
void left_pos(list* node) {
    if (node->pos == 1) {
        return;
    }
    node->pos+= 1;
    left_pos(node->left);
}
// find node to position
stack* findDataFromPosition(list* left, list* right, int pos) {
    if (left->pos == pos) {
        return left->data;
    } else if (right->pos == pos) {
        return right->data;
    } else {
        return findDataFromPosition(left->left, right->right, pos);
    }
}
__declspec(dllexport) stack* makeStack() {
    stack* tmp = (stack*)malloc(sizeof(stack));
    tmp->txt = NULL;
    tmp->node = NULL;
    return tmp;
}
__declspec(dllexport) stack* push(stack* st, wchar_t* txt) {
    if (st == NULL) {
        st = makeStack();
        st->txt = _wcsdup(txt);
        return st;
    }
    else if (st->txt == NULL) {
        st->txt = _wcsdup(txt);
        return st;
    }
    else {
        stack* tmp = (stack*)malloc(sizeof(stack));
        tmp->node = st;
        tmp->txt = _wcsdup(txt);
        return tmp;
    }
}
__declspec(dllexport) wchar_t* pop(stack** st){
    if (st == NULL || *st == NULL)
        return _wcsdup(L"None");
    wchar_t* t = (*st)->txt;
    stack* tmp = (*st);
    *st = ((*st)->node);
    free(tmp);
 
    return t;
}
_declspec(dllexport) stack* copy(stack* st){
    stack* newNode = (stack*)malloc(sizeof(stack));
    if (st->node == NULL){
        memcpy(newNode, st, sizeof(stack));
    } else {
        newNode->txt = st->txt;
        newNode->node = copy(st->node);
    }
    return newNode;
}
__declspec(dllexport) stack* getPtr(stack* st){
    return st;
}
__declspec(dllexport) void freeStack(stack* st) {
    free(st);
}
__declspec(dllexport) list* makeList(){
    list* tmp = (list*)malloc(sizeof(list));
    tmp->data = NULL;
    tmp->left = NULL;
    tmp->right = NULL;
    tmp->pos = 1;
    return tmp;
}
__declspec(dllexport) list* appendNode(list* n, stack* data) {
    if (data == NULL) {
        return NULL;
    } if (n == NULL) {
        n = (list*)malloc(sizeof(list));
        n->data = data;
        n->left = NULL;
        n->right = NULL;
        n->pos = 1;
    } else if (n->data == NULL) {
        n->data = data;
        n->left = NULL;
        n->right = NULL;
        n->pos = 1;
    } else if (n->left == NULL) {
        list* tmp = (list*)malloc(sizeof(list));
        tmp->right = n;
        n->left = tmp;
        tmp->left = n;
        n->right = tmp;
        tmp->data = data;
        tmp->pos = n->pos + 1;
    } else {
        list* tmp = n->right;
        list* ttmp = (list*)malloc(sizeof(list));
        ttmp->data = data;
        ttmp->pos = tmp->pos + 1;
        n->right = ttmp;
        ttmp->left = n;
        ttmp->right = tmp;
        tmp->left = ttmp;
    }
    return n;
}
__declspec(dllexport) list* getLeft(list* n) {
    if (n == NULL) {
        return NULL;
    } if (n->left == NULL) {
        return NULL;
    } else if (n->left->pos == 1) {
        return NULL;
    }
    return n->left;
}
__declspec(dllexport) list* getRight(list* n) {
    if (n->right == NULL) {
        return n;
    } else if (n->right->pos == 1) {
        return NULL;
    }
    return n->right;
}
__declspec(dllexport) bool isStart(list* n) {
    if (n == NULL) {
        return false;
    }
    else if (n->pos == 1) {
        return true;
    }
    else {
        return false;
    }
}
__declspec(dllexport) stack* getData(list* n) {
    return n->data;
}
__declspec(dllexport) int len(list* n) {
    if (n == NULL) {
        return 0;
    } else if (n->data == NULL) {
        return 0;
    } else if (n->right == NULL | n->left == NULL) {
        return 1;
    } else {
        return n->right->pos;
    }
}
__declspec(dllexport) int pos(list* n) {
    if (n == NULL) {
        return 0;
    } else if (n->right == NULL & n->left == NULL & n != NULL) {
        return 1;
    } else if (n->right == NULL | n->left == NULL){
        return -1;
    } else {
        return n->pos;
    }
}
__declspec(dllexport) bool leftNone(list* n){
    if (n == NULL) {
        return true;
    }
    if (n->left == NULL) {
        return true;
    }
    return false;
}
__declspec(dllexport) bool rightNone(list* n){
    if (n->right == NULL) {
        return true;
    }
    return false;
}
__declspec(dllexport) list* appendForward(list* n, stack* data) {
    if (n == NULL) {
        n = (list*)malloc(sizeof(list));
        n->data = data;
        n->pos = 1;
        n->left = NULL;
        n->right = NULL;
        return n;
    } else if (n->right == NULL & n->left == NULL) {
        list* tmp = (list*)malloc(sizeof(list));
        tmp->left = n;
        tmp->right = n;
        n->left = tmp
        n->right = tmp;
        return tmp;
    }
    list* tmp = (list*)malloc(sizeof(list));
    tmp->left = n->left
    n->left->right = tmp;
    tmp->right = n;
    n->left = tmp;
    return n;
}
__declspec(dllexport) bool posCheck(list* n, int pos) {
    if (n->pos == pos) {
        return true;
    }
    return false;
}
bool compareStack(stack* search_data, stack* comparision_target) {
    bool compare_value = true;
    if (search_data->node == NULL & comparision_target->node == NULL) {
        compare_value = true;
    } else {
        compare_value = false;
    }
    if (wcscmp(search_data->txt, comparision_target->txt) == 0){
        if (compare_value) {
            return true;
        } else if ((comparision_target->node == NULL & search_data->node != NULL) | (comparision_target->node != NULL & search_data->node == NULL)) {
            return false;
        } else if (comparision_target->node != NULL & search_data->node != NULL) {
            return compareStack(search_data->node, comparision_target->node);
        }
    }
    return false;
}
// 0 is no data,
// -1 is unknown error
__declspec(dllexport) int findPositionFromData(list* left, list* right, stack* data) {
    if (compareStack(left->data, data)) {
        return left->pos;
    } else if (compareStack(right->data, data)) {
        return right->pos;
    } else if (right->pos < left->pos) {
        return 0;
    } else if (left->pos != right->pos) {
        return findPositionFromData(left->left, right->right, data);
    } else {
        return -1;
    }
}
__declspec(dllexport) int appendLeft(list* left, stack* data, int pos) {
    if (left == NULL) {
        return -1;
    } else if(left->left == NULL) {
        return -2;
    } else if (data == NULL) {
        return -3;
    }
    if (left->pos == pos) {
        list* tmp = left;
        list* ttmp = left->left;
        list* stmp = (list*)malloc(sizeof(list));
        stmp->pos = tmp->pos + 1;
        stmp->data = data;
        stmp->right = tmp;
        tmp->left = stmp;
        ttmp->right = stmp;
        stmp->left = ttmp;
        left_pos(ttmp);
        return stmp->pos;
    }
    return appendLeft(left->left, data, pos);
}
__declspec(dllexport) int appendRight(list* right, stack* data, int pos) {
    if (right == NULL) {
        return -1;
    } else if (right->right == NULL) {
        return -2;
    } else if (data == NULL) {
        return -3;
    }
    if (right->pos == pos) {
        list* tmp = right;
        list* ttmp = right->right;
        list* stmp = (list*)malloc(sizeof(list));
        stmp->pos = tmp->pos + 1;
        stmp->data = data;
        stmp->right = ttmp;
        ttmp->left = stmp;
        tmp->right = stmp;
        stmp->left = stmp;
        left_pos(tmp);
        return stmp->pos;
    }
    return appendRight(right->right, data, pos);
}
__declspec(dllexport) void freeList(list* n) {
    if (n == NULL) return;
    else if (n->data == NULL){ free(n); return; }
    list* tmp = n->left;
    if (tmp) tmp->right = NULL;
    free(n);
    freeList(tmp);
}