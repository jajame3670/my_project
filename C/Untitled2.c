#include <stdio.h>
int a, b;
main() {
    printf("Enter A: ");
    scanf("%d", &a);
    printf("Enter B: ");
    scanf("%d", &b);
 while(a==b){
 	printf("A=b ,try againt\n");
 	 printf("Enter A: ");
    scanf("%d", &a);
    printf("Enter B: ");
    scanf("%d", &b);
 }
    if (a > b) {
        printf("A is bigger than B\n");
        printf("%d > %d\n", a, b);
    } 
    else if (a < b){
        printf("B is bigger than A\n");
        printf("%d < %d\n", a, b);
    } 
}
