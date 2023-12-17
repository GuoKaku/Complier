#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 100

typedef struct {
    int top;
    int items[MAX_SIZE];
} Stack;

void push(Stack* stack, int item) {
    if (stack->top == MAX_SIZE - 1) {
        printf("栈已满\n");
    } else {
        stack->items[++stack->top] = item;
    }
}

int pop(Stack* stack) {
    if (stack->top == -1) {
        printf("栈为空\n");
        return -1;
    } else {
        return stack->items[stack->top--];
    }
}

int isOperator(char c) {
    return (c == '+' || c == '-' || c == '*' || c == '/');
}

int performOperation(int operand1, int operand2, char m_operator) {
    switch (m_operator) {
        case '+':
            return operand1 + operand2;
        case '-':
            return operand1 - operand2;
        case '*':
            return operand1 * operand2;
        case '/':
            return operand1 / operand2;
        default:
            return 0;
    }
}

int evaluateExpression(const char* expression) {
    Stack stack;
    stack.top = -1;

    for (int i = 0; i < strlen(expression); i++) {
        if (expression[i] == ' ' || expression[i] == ',') {
            continue;
        } else if (isOperator(expression[i])) {
            int operand2 = pop(&stack);
            int operand1 = pop(&stack);
            int result = performOperation(operand1, operand2, expression[i]);
            push(&stack, result);
        } else if (expression[i] >= '0' && expression[i] <= '9') {
            int operand = 0;
            while (i < strlen(expression) && expression[i] >= '0' && expression[i] <= '9') {
                operand = (operand * 10) + (expression[i] - '0');
                i++;
            }
            i--;
            push(&stack, operand);
        }
    }

    return pop(&stack);
}

int main() {
    char expression[100];
    printf("请输入一个四则运算表达式: ");
    fgets(expression, sizeof(expression), stdin);
    expression[strcspn(expression, "\n")] = '\0';

    int result = evaluateExpression(expression);

    printf("表达式的值为: %d\n", result);

    return 0;
}
