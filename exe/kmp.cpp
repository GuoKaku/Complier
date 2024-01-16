#include <string.h>
#include <stdio.h>

char text[4096], pattern[4096];
int next[4096];

void getnext(){
    next[0] = -1;
    int i = 0, j = -1;
    while (i < strlen(pattern) - 1){
        if ((j == -1) || (pattern[i] == pattern[j]))
        {
            i = i + 1;
            j = j + 1;
            if (pattern[i] == pattern[j])
                next[i] = next[j];
            else
                next[i] = j;
        }
        else
            j = next[j];
    }
    return;
}

int kmp(int start){
    int p_len = strlen(pattern), t_len = strlen(text), i = start, j = 0;
    while ((i < t_len) && (j < p_len))
    {
        if ((j == -1) || (text[i] == pattern[j])){
            i = i + 1;
            j = j + 1;
        }
        else
            j = next[j];
    }
    if (j == p_len)
        return i - j;
    else
        return -1;
    return -1;
}

int main(){
    printf("Enter the text here: ");
    gets(text);
    printf("Enter the pattern here: ");
    gets(pattern);
    getnext();

    int start = 0, i = 0, note = 0, len = strlen(text);
    while (start < len){
        i = kmp(start);
        if (i != -1){
            printf("position: %d\n", i + 1);
            start = i + 1;
            note = 1;
        }
        else
            break;
    }
    if (!note)
        printf("there is no pattern in text");
    return 0;
}
