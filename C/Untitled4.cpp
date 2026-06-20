#include <stdio.h>
int choice;
main() {
    printf("MAIN MENU\n");
    printf("1. Menu 1\n");
    printf("2. Menu 2\n");
    printf("3. Menu 3\n");
    printf("4. Menu 4\n");
    printf("=====================\n");
    printf("Enter your choice: ");
    scanf("%d", &choice);
    switch(choice) {
        case 1:
            printf("You chose Menu 1\n");
            break;
        case 2:
            printf("You chose Menu 2\n");
            break;
        case 3:
            printf("You chose Menu 3\n");
            break;
        case 4:
            printf("You chose Menu 4\n");
            break;
        default:
            printf("Invalid choice! Program closing...\n");
    }
    printf("Program closed.\n");
}

