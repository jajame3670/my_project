#include <stdio.h>
#define MAX_SIZE 100
int input(int arr[], int max_size) {
    int n,i;
    printf("type number: ");
    scanf("%d", &n);
    if (n > max_size)
        n = max_size;
    printf("you input: %d\n", n);
    for (i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }

    return n;
}

void sort(int arr[], int n) {
	int i,j;
    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

void output(int arr[], int n) {
	int i;
    printf("result: ");
    for (i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
}

int main() {
    int arr[MAX_SIZE];
    int n;
	n = input(arr, MAX_SIZE);
    sort(arr, n);
    output(arr, n);
}

