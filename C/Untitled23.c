#include <stdio.h>
int numbers[10]={23,12,45,15,9,25,33,40,18,4}, max,i;
main(){
	max= numbers[0];
	for (i=1;i<10;i++) {
		if(numbers[i]>max){
		max=numbers[i];
		}
	}
	printf(" max is: %d\n",max);
}

