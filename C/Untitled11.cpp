#include <stdio.h>
int main() {
    float X[500], t;
    int N, i, k;
    char ch;
    printf("Bubble Sort for maximum data 500\n");
    printf("Input number of data: ");
    scanf("%d", &N);
    printf("Input data:\n");
    for (i = 0; i < N; i++) {
        scanf("%f", &X[i]);
    }
    do {
        ch = 'N';
        for (i = 0; i < N - 1; i++) {
            if (X[i] > X[i + 1]) {
                t = X[i];
                X[i] = X[i + 1];
                X[i + 1] = t;
                ch = 'S';
            }
        }
    } while (ch == 'S');
    for (k = 0; k < N; k++) {
        printf("%.2f\n", X[k]);
        
    }
}

