pragma solidity 0.6.4;

contract Library {

    function search(int[] memory arr, uint arr_len, int x) public pure returns(int){  
	    for (uint i = 0; i < arr_len; i++) 
	    if(arr[uint(i)] == x) 
		  return int(i); 
	    return -1; 
	}
	
	function factorial(int num) public pure returns(int){
        int copyNum = num;
	    int fact = 1;
	    if(num < 0)
		    fact = -1;
	    else if(num > 1){
		    while(num > 1){
		        fact = fact * num--;
		    }
	    }
	    return fact==verifyFactorial(copyNum)?fact:-2;
	}

	function verifyFactorial(int num) public pure returns(int){
	    int fact = 1;
	    if(num < 0){
		    fact = -1;
	    }
	    else if(num > 1){ 
		    do{
	            fact = fact * num;
	            num = num - 1;
		     }while(num>1);
	    }
	    else{
	        fact = 1;
	    }
	    return fact;	
	}
}
