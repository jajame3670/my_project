#include <stdio.h>
    float score, sum = 0, avg;
    int i;
int main() {
    printf("Enter scores for 12 subjects:\n");
    for (i = 1; i <= 12; i++) {
        printf("Subject %d: ", i);
        scanf("%f", &score);
        sum += score;
    }
    avg = sum / 12;
    printf("Total Score  = %.2f\n", sum);
    printf("Average Score = %.2f\n", avg);
}

