#include "leader.h"
#include <stdio.h>
#include <iostream>
#include<sys/socket.h>
using namespace std;


Leader::Leader(std::string followerAddr[], int follower_num){
	this.followersAddr = followerAddr;
	this.follower_num = follower_num;
}


Leader::~Leader(){

}


void updateMap(){

}


void sendUpdateCommand(){

}
// maybe use broadcast


map<std::string, std::string> lockMap;


bool isConnected(){


}
// connection status with leader server
// could use an array to store the ip address of 
// all the follower servers which have a connection
// with this leader server