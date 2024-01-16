#include <stdio.h>
#include <string.h>

// 计算next数组
void compute_next(char* pattern, int* next) {
    int i, j;
    int m = strlen(pattern);
    next[0] = -1; // 初始化
    for (i = 1, j = -1; i < m; i++) {
        while (j >= 0 && pattern[i] != pattern[j + 1]) {
            j = next[j];
        }
        if (pattern[i] == pattern[j + 1]) {
            j++;
        }
        next[i] = j;
    }
}

// KMP算法
int kmp(char* text, char* pattern, int* next) {
    int i, j;
    int n = strlen(text);
    int m = strlen(pattern);
    for (i = 0, j = -1; i < n; i++) {
        while (j >= 0 && text[i] != pattern[j + 1]) {
            j = next[j];
        }
        if (text[i] == pattern[j + 1]) {
            j++;
        }
        if (j == m - 1) { // 匹配成功
            return i - j;
        }
    }
    return -1; // 匹配失败
}

int main() {
    char text[100];
    char pattern[100];

    printf("请输入文本串: ");
    fgets(text, 100, stdin);
    text[strcspn(text, "\n")] = '\0'; // 去除末尾的换行符

    printf("请输入模式串: ");
    fgets(pattern, 1000, stdin);
    pattern[strcspn(pattern, "\n")] = '\0'; // 去除末尾的换行符

    int next[9999];
    compute_next(pattern, next);
    int pos = kmp(text, pattern, next);
    if (pos != -1) {
        printf("模式串在位置 %d 处匹配成功\n", pos);
    } else {
        printf("模式串未找到\n");
    }
    return 0;
}
