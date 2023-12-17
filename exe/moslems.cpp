#include <stdio.h>
#include <string.h>
#include <ctype.h>

int isPalindrome(char* s) {
    int len = strlen(s);
    int i, j;
    
    // 去除字符串中的非字母和数字字符，并转换为小写字母
    char cleanString[9999];
    int cleanLen = 0;
    for (i = 0; i < len; i++) {
        if ((s[i] >= 'a' && s[i] <= 'z') || (s[i] >= 'A' && s[i] <= 'Z') || (s[i] >= '0' && s[i] <= '9')) {
            cleanString[cleanLen++] = tolower(s[i]);
        }
    }
    cleanString[cleanLen] = '\0';
    
    // 判断是否为回文
    int left = 0;
    int right = cleanLen - 1;
    while (left < right) {
        if (cleanString[left] != cleanString[right]) {
            return 0; // 不是回文
        }
        left++;
        right--;
    }
    
    return 1; // 是回文
}

int main() {
    char s[100];
    
    printf("请输入一个字符串: ");
    fgets(s, sizeof(s), stdin);
    s[strcspn(s, "\n")] = '\0'; // 去除末尾的换行符
    
    if (isPalindrome(s)) {
        printf("True\n");
    } else {
        printf("False\n");
    }
    
    return 0;
}
