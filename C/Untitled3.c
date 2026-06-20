#include <stdio.h>
    int n, i;
    float price, qty, subtotal, total = 0;
int main() {
    printf("Enter number of items: ");
    scanf("%d", &n);
    for(i = 1; i <= n; i++) {
        printf("\nItem %d\n", i);
        printf("Enter price: ");
        scanf("%f", &price);
        printf("Enter quantity: ");
        scanf("%f", &qty);

        subtotal = price * qty;
        total += subtotal;

        printf("Subtotal for item %d: %.2f\n", i, subtotal);
    }
    printf("Total price of all items: %.2f\n", total);
}

