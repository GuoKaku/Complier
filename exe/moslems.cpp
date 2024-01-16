#include <iostream>
#include <string.h>

int main(){
	int n = 0, i = 0;
	char a[2048];
	printf("Please enter a string\n");
	gets(a);
	n=strlen(a);
	while(i<n){
	    if (a[i] != a[(n - i) - 1]) {
			printf("this string is not a language of the Moslems.\n");
			return 0;
		}
		i=i+1;
	}
	printf("this string is a language of the Moslems.\n");
	return 0;
}
