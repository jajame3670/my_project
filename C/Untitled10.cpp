#include <stdio.h>

int main() {
    float X[500], t;
    int N, i, j;
    printf("Select sort (max data = 500)\n");
    printf("Input number of data: ");
    scanf("%d", &N);
    if (N > 500 || N <= 0) {
	 return 0;
    }
    printf("Input data:\n");
    for (i = 0; i < N; i++) {
        scanf("%f", &X[i]);
    }
    for (i = 0; i < N - 1; i++) {
        for (j = i + 1; j < N; j++) {
            if (X[j] < X[i]) {
                t = X[j];
                X[j] = X[i];
                X[i] = t;
            }
        }
    }
    printf("Sorted data:\n");
    for (i = 0; i < N; i++) {
        printf("%f\n", X[i]);
    }
}

