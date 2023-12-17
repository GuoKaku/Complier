#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void sort(int* arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main() {
    char input[100];
    printf("请输入若干个整数，用逗号分隔: ");
    fgets(input, sizeof(input), stdin);
    input[strcspn(input, "\n")] = '\0';

    int arr[100];
    int n = 0;
    char* token = strtok(input, ",");
    while (token != NULL) {
        arr[n++] = atoi(token);
        token = strtok(NULL, ",");
    }

    sort(arr, n);

    printf("排序后的结果为: ");
    for (int i = 0; i < n; i++) {
        printf("%d", arr[i]);
        if (i != n - 1) {
            printf(", ");
        }
    }
    printf("\n");

    return 0;
}
