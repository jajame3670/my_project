#include <stdio.h>
void Input_Data(float *, int);
void Selection_Sort(float *, int);
void Output_Data(float *, int);
void Swap(float *, float *);
int main() {
    float X[5000];
    int N;
    printf("Selection Sort for maximum data 5000\n");
    printf("Input number of data: ");
    scanf("%d", &N);
    printf("Input data:\n");
    Input_Data(X, N);
    Selection_Sort(X, N);
    Output_Data(X, N);
}
void Input_Data(float *a, int num) {
	int i;
    for ( i = 1; i <= num; i++) {
        scanf("%f", &a[i]);
    }
}
void Selection_Sort(float *b, int nm) {
	int i;
    for (i = 1; i <= nm - 1; i++) {
        for (int j = i + 1; j <= nm; j++) {
            if (b[i] > b[j]) {
                Swap(&b[i], &b[j]);
            }
        }
    }
}
void Swap(float *p, float *q) {
    float t = *p;
    *p = *q;
    *q = t;
}
void Output_Data(float *c, int nn) {
    for (int k = 1; k <= nn; k++) {
        printf("%f\n", c[k]);
    }
}

